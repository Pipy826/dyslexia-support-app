from typing import Dict, List
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..models.screening import Screening, DimensionScore, Report
from ..models.child import Child


def calculate_score(answers: List[Dict], game_type: str) -> tuple[int, List[Dict]]:
    """计算筛查评分，返回总分和各维度分数"""
    if not answers:
        return 0, []

    total_count = len(answers)
    correct_count = sum(1 for a in answers if a.get("is_correct", False))
    total_score = int((correct_count / total_count) * 100) if total_count > 0 else 0

    # 根据游戏类型映射到能力维度
    dimension_map = {
        "visual": ["visual_discrimination", "attention"],
        "spelling": ["phonological", "character_order", "spelling"],
        "comprehension": ["reading_comprehension", "semantic_integration", "information_extraction"]
    }

    dimensions = dimension_map.get(game_type, ["general"])

    # 将答题记录按顺序分配到各维度，计算各维度独立得分
    dimension_scores = []
    n_dims = len(dimensions)
    chunk = max(1, total_count // n_dims)

    for i, dim in enumerate(dimensions):
        start = i * chunk
        # 最后一个维度取剩余所有题目
        end = start + chunk if i < n_dims - 1 else total_count
        dim_answers = answers[start:end]
        if dim_answers:
            dim_correct = sum(1 for a in dim_answers if a.get("is_correct", False))
            dim_score = int((dim_correct / len(dim_answers)) * 100)
        else:
            # 题目不足时用总分兜底
            dim_score = total_score
        dimension_scores.append({"dimension": dim, "score": dim_score})

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


def generate_summary(child_name: str, age: int, risk_level: str, scores: Dict[str, int]) -> str:
    """生成评估摘要"""
    risk_descriptions = {
        "low": f"{child_name}的读写能力发展正常，各项能力指标均在正常范围内。建议继续保持良好的学习习惯。",
        "medium": f"{child_name}在某些能力维度上需要关注，可能存在轻微的读写困难。建议家长多加陪伴和引导。",
        "high": f"{child_name}的评估结果显示存在明显的读写困难特征，建议寻求专业的评估和干预支持。"
    }
    return risk_descriptions.get(risk_level, "")


def generate_recommendations(risk_level: str, scores: Dict[str, int]) -> str:
    """生成干预建议"""
    recommendations = {
        "low": [
            "保持每日阅读习惯",
            "鼓励孩子多写字、多表达",
            "定期进行简单的读写游戏"
        ],
        "medium": [
            "加强视觉辨识训练，如找不同游戏",
            "每日进行10-15分钟拼字练习",
            "家长陪伴进行亲子共读",
            "建议每月进行一次能力评估"
        ],
        "high": [
            "建议寻求专业机构的全面评估",
            "制定个性化的训练计划",
            "家长学习相关干预方法",
            "定期跟踪能力发展变化",
            "必要时咨询语言治疗师"
        ]
    }

    recs = recommendations.get(risk_level, recommendations["medium"])
    return "；".join(recs) + "。"


def create_screening_report(
    db: Session,
    child_id: int,
    screening_id: int,
    game_type: str,
    answers: List[Dict]
) -> Report:
    """创建筛查报告"""
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
            score=ds["score"]
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

    # 生成报告
    summary = generate_summary(child.name, age, risk_level, scores_dict)
    recommendations = generate_recommendations(risk_level, scores_dict)

    report = Report(
        child_id=child_id,
        screening_id=screening_id,
        overall_score=total_score,
        risk_level=risk_level,
        summary=summary,
        recommendations=recommendations,
        dimensions=json.dumps(scores_dict, ensure_ascii=False)
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report
