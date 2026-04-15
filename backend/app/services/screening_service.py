"""
筛查评分服务
- 计算各维度得分
- 判定风险等级
- 生成筛查报告（AI 个性化解读 + 降级模板）
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from datetime import datetime
import json
import asyncio

from ..models.screening import Screening, DimensionScore, Report
from ..models.child import Child


# ── 评分计算 ─────────────────────────────────────────────────────────────────

def calculate_score(answers: List[Dict], game_type: str) -> tuple:
    """计算筛查评分，返回 (总分, 各维度分数列表)"""
    if not answers:
        return 0, []

    correct_count = sum(1 for a in answers if a.get("is_correct", False))
    total_count = len(answers)
    total_score = int((correct_count / total_count) * 100) if total_count > 0 else 0

    # 游戏类型 → 能力维度映射
    dimension_map = {
        "visual": ["visual_discrimination", "attention"],
        "spelling": ["spelling", "phonological", "character_order"],
        "comprehension": ["reading_comprehension", "semantic_integration", "information_extraction"]
    }

    dimensions = dimension_map.get(game_type, ["general"])

    # 根据答题时间计算注意力维度（反应越快越稳定，注意力越好）
    dimension_scores = []
    for dim in dimensions:
        if dim == "attention" and answers:
            # 用答题时间稳定性估算注意力
            times = [a.get("time_spent", 5) for a in answers if a.get("time_spent")]
            if times:
                avg_time = sum(times) / len(times)
                # 时间在合理范围内（2-8秒）且稳定，注意力得分高
                attention_score = min(100, max(0, int(100 - abs(avg_time - 4) * 5)))
                dimension_scores.append({"dimension": dim, "score": attention_score})
            else:
                dimension_scores.append({"dimension": dim, "score": total_score})
        else:
            dimension_scores.append({"dimension": dim, "score": total_score})

    return total_score, dimension_scores


def determine_risk_level(scores: Dict[str, int]) -> str:
    """根据各维度评分确定风险等级"""
    if not scores:
        return "medium"

    avg_score = sum(scores.values()) / len(scores)
    low_dims = [k for k, v in scores.items() if v < 60]

    if avg_score >= 75 and len(low_dims) == 0:
        return "low"
    elif avg_score >= 60 or len(low_dims) <= 1:
        return "medium"
    else:
        return "high"


# ── 报告文字生成（模板降级） ──────────────────────────────────────────────────

def generate_summary(child_name: str, age: int, risk_level: str, scores: Dict[str, int]) -> str:
    """生成评估摘要（模板版，AI 版在 ai_service.py）"""
    risk_descriptions = {
        "low": f"{child_name}的读写能力发展正常，各项能力指标均在正常范围内。建议继续保持良好的学习习惯。",
        "medium": f"{child_name}在某些能力维度上需要关注，可能存在轻微的读写困难。建议家长多加陪伴和引导。",
        "high": f"{child_name}的评估结果显示存在明显的读写困难特征，建议寻求专业的评估和干预支持。",
    }
    return risk_descriptions.get(risk_level, "")


def generate_recommendations(risk_level: str, scores: Dict[str, int] = None) -> str:
    """生成干预建议（模板版）"""
    recommendations = {
        "low": ["保持每日阅读习惯", "鼓励孩子多写字、多表达", "定期进行简单的读写游戏"],
        "medium": [
            "加强视觉辨识训练，如找不同游戏",
            "每日进行10-15分钟拼字练习",
            "家长陪伴进行亲子共读",
            "建议每月进行一次能力评估",
        ],
        "high": [
            "建议寻求专业机构的全面评估",
            "制定个性化的训练计划",
            "家长学习相关干预方法",
            "定期跟踪能力发展变化",
            "必要时咨询语言治疗师",
        ],
    }
    recs = recommendations.get(risk_level, recommendations["medium"])
    return "；".join(recs) + "。"


# ── 报告创建（同步版，供 screening API 调用） ─────────────────────────────────

def create_screening_report(
    db: Session,
    child_id: int,
    screening_id: int,
    game_type: str,
    answers: List[Dict],
) -> Report:
    """
    创建筛查报告（同步版）。
    summary 先用模板填充，前端可随后调用 /api/ai/report-interpretation 获取 AI 解读。
    """
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError("Child not found")

    # 计算年龄
    today = datetime.now().date()
    age = today.year - child.birth_date.year - (
        (today.month, today.day) < (child.birth_date.month, child.birth_date.day)
    )

    # 计算评分
    total_score, dimension_scores = calculate_score(answers, game_type)

    # 创建维度评分记录
    for ds in dimension_scores:
        dim_score = DimensionScore(
            screening_id=screening_id,
            dimension=ds["dimension"],
            score=ds["score"],
        )
        db.add(dim_score)

    # 确定风险等级
    scores_dict = {ds["dimension"]: ds["score"] for ds in dimension_scores}
    risk_level = determine_risk_level(scores_dict)

    # 更新筛查记录
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if screening:
        screening.score = total_score
        screening.risk_level = risk_level
        screening.completed_at = datetime.utcnow()

    # 生成报告（模板版 summary，AI 解读通过独立接口获取）
    summary = generate_summary(child.name, age, risk_level, scores_dict)
    recommendations = generate_recommendations(risk_level, scores_dict)

    report = Report(
        child_id=child_id,
        screening_id=screening_id,
        overall_score=total_score,
        risk_level=risk_level,
        summary=summary,
        recommendations=recommendations,
        dimensions=json.dumps(scores_dict, ensure_ascii=False),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report


async def create_screening_report_async(
    db: Session,
    child_id: int,
    screening_id: int,
    game_type: str,
    answers: List[Dict],
) -> Report:
    """
    创建筛查报告（异步版）。
    summary 由 AI 生成，如果 AI 调用失败则降级到模板。
    """
    from ..services.ai_service import generate_report_interpretation

    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError("Child not found")

    today = datetime.now().date()
    age = today.year - child.birth_date.year - (
        (today.month, today.day) < (child.birth_date.month, child.birth_date.day)
    )

    total_score, dimension_scores = calculate_score(answers, game_type)

    for ds in dimension_scores:
        dim_score = DimensionScore(
            screening_id=screening_id,
            dimension=ds["dimension"],
            score=ds["score"],
        )
        db.add(dim_score)

    scores_dict = {ds["dimension"]: ds["score"] for ds in dimension_scores}
    risk_level = determine_risk_level(scores_dict)

    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if screening:
        screening.score = total_score
        screening.risk_level = risk_level
        screening.completed_at = datetime.utcnow()

    # AI 生成 summary
    try:
        summary = await generate_report_interpretation(
            child_name=child.name,
            child_age=age,
            risk_level=risk_level,
            overall_score=total_score,
            dimensions=scores_dict,
        )
    except Exception:
        summary = generate_summary(child.name, age, risk_level, scores_dict)

    recommendations = generate_recommendations(risk_level, scores_dict)

    report = Report(
        child_id=child_id,
        screening_id=screening_id,
        overall_score=total_score,
        risk_level=risk_level,
        summary=summary,
        recommendations=recommendations,
        dimensions=json.dumps(scores_dict, ensure_ascii=False),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report
