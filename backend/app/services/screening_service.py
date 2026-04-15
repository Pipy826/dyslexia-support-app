from typing import Dict, List
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..models.screening import Screening, DimensionScore, Report
from ..models.child import Child


def calculate_score(answers: List[Dict], game_type: str) -> tuple[int, List[Dict]]:
    """计算筛查评分，返回总分和各维度分数
    
    综合考虑：正确率（70%权重）+ 行为质量（30%权重）
    行为质量：反应时间过慢、修改次数多、超时多 会降低行为分
    """
    if not answers:
        return 0, []

    total_count = len(answers)
    correct_count = sum(1 for a in answers if a.get("is_correct", False))
    accuracy_score = int((correct_count / total_count) * 100) if total_count > 0 else 0

    # 行为质量评分（0-100）
    behavior_penalties = 0
    for a in answers:
        if a.get("is_timeout"):
            behavior_penalties += 3          # 超时扣3分
        change_count = a.get("change_count") or 0
        if change_count >= 2:
            behavior_penalties += 2          # 多次修改扣2分
        reaction_time = a.get("reaction_time")
        if reaction_time and reaction_time > 8000:
            behavior_penalties += 1          # 反应超8秒扣1分

    behavior_score = max(0, 100 - behavior_penalties)

    # 综合评分：正确率70% + 行为质量30%
    total_score = int(accuracy_score * 0.7 + behavior_score * 0.3)
    total_score = max(0, min(100, total_score))

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
    """生成评估摘要，包含具体弱项说明"""
    dim_names = {
        "visual_discrimination": "视觉辨识",
        "attention":             "持续注意力",
        "phonological":          "音形映射",
        "character_order":       "字序组织",
        "spelling":              "拼写输出",
        "reading_comprehension": "阅读理解",
        "semantic_integration":  "语义整合",
        "information_extraction":"信息提取",
    }

    weak_dims = [dim_names.get(d, d) for d, s in scores.items() if s < 60]
    strong_dims = [dim_names.get(d, d) for d, s in scores.items() if s >= 75]

    if risk_level == "low":
        base = f"{child_name}的读写能力发展正常，各项能力指标均在正常范围内。"
        if strong_dims:
            base += f"其中{'/'.join(strong_dims[:2])}表现尤为突出。"
        base += "建议继续保持良好的学习习惯。"
        return base

    if risk_level == "medium":
        base = f"{child_name}整体读写能力基本正常，但存在一定的短板需要关注。"
        if weak_dims:
            base += f"在{'/'.join(weak_dims)}方面表现偏弱，可能影响日常读写效率。"
        base += "建议家长多加陪伴和针对性引导。"
        return base

    # high
    base = f"{child_name}的评估结果显示存在明显的读写困难特征。"
    if weak_dims:
        base += f"在{'/'.join(weak_dims)}等多个维度表现明显偏弱，"
    base += "建议尽快寻求专业的评估和干预支持，避免错过最佳干预窗口期。"
    return base


def generate_recommendations(risk_level: str, scores: Dict[str, int]) -> str:
    """生成干预建议，针对具体弱项维度给出专项建议"""
    dim_advice = {
        "visual_discrimination": "每天进行5-10分钟的形近字辨别练习，如找不同、圈错字游戏",
        "attention":             "将训练时间控制在10-15分钟内，使用计时器帮助孩子建立专注节奏",
        "phonological":          "多做拼音与汉字对应练习，可用卡片游戏加强音形联结",
        "character_order":       "练习汉字笔顺，用描红或临写方式强化字形记忆",
        "spelling":              "每日听写5个词语，错误的词语重复练习3遍",
        "reading_comprehension": "亲子共读后提问，引导孩子用自己的话复述故事",
        "semantic_integration":  "多做造句练习，帮助孩子理解词语在句子中的意思",
        "information_extraction":"阅读后让孩子找出关键信息，如时间、地点、人物",
    }

    # 找出弱项维度（得分 < 70）
    weak_dims = [dim for dim, score in scores.items() if score < 70]
    strong_dims = [dim for dim, score in scores.items() if score >= 75]

    parts = []

    # 弱项专项建议
    if weak_dims:
        weak_advices = [dim_advice[d] for d in weak_dims if d in dim_advice]
        if weak_advices:
            parts.append("重点训练方向：" + "；".join(weak_advices))

    # 通用建议（按风险等级）
    general = {
        "low":    "整体表现良好，保持每日阅读习惯，定期进行简单的读写游戏即可",
        "medium": "建议每天安排10-15分钟专项训练，家长陪伴进行，每月复评一次",
        "high":   "建议制定系统性训练计划，同时考虑寻求专业机构的全面评估与指导",
    }
    parts.append(general.get(risk_level, general["medium"]))

    return "。".join(parts) + "。"


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
    if child.birth_date:
        age = today.year - child.birth_date.year - (
            (today.month, today.day) < (child.birth_date.month, child.birth_date.day)
        )
    else:
        age = 8  # 默认年龄

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
