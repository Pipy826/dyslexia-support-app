"""
筛查评分服务
- 计算各维度得分
- 判定风险等级
- 生成筛查报告文字（模板降级）
"""

from typing import Dict, List
from datetime import datetime
import json

# ── 评分计算 ─────────────────────────────────────────────────────────────────

# 各难度等级对应的"宽松基准时限"（秒），用于效率分归一化
# 超出基准时限才开始扣效率分，在基准内完成则满分
_DIFFICULTY_BASE_TIME = {"L1": 10.0, "L2": 8.0, "L3": 6.0}
_DEFAULT_BASE_TIME = 10.0


def _calc_efficiency_score(answers: List[Dict]) -> int:
    """
    效率分 = 综合正确率与反应时的加权得分（0-100）。

    公式：
      - 正确率分（权重 0.6）：correct_count / total * 100
      - 反应时分（权重 0.4）：对每道答对的题，用时越短得分越高；
        用时 ≤ 基准时限 50% → 满分；用时 = 基准时限 → 60分；超时 → 0分。
        答错或超时的题反应时分计 0。

    这样既奖励答对，也奖励答得快，符合"效率 = 正确率 × 速度"的直觉。
    """
    if not answers:
        return 0

    total = len(answers)
    correct_count = sum(1 for a in answers if a.get("is_correct", False))
    accuracy_score = (correct_count / total) * 100

    rt_scores = []
    for a in answers:
        if not a.get("is_correct", False) or a.get("is_timeout", False):
            rt_scores.append(0)
            continue
        time_spent = a.get("time_spent") or 0
        # 从题目难度推断基准时限（答题记录里没有直接存 difficulty，用 time_limit 字段）
        base_time = float(a.get("time_limit", _DEFAULT_BASE_TIME) or _DEFAULT_BASE_TIME)
        if time_spent <= base_time * 0.5:
            rt_scores.append(100)
        elif time_spent <= base_time:
            # 线性插值：[base*0.5, base] → [100, 60]
            ratio = (time_spent - base_time * 0.5) / (base_time * 0.5)
            rt_scores.append(int(100 - ratio * 40))
        else:
            rt_scores.append(0)

    avg_rt_score = sum(rt_scores) / len(rt_scores) if rt_scores else 0
    efficiency = accuracy_score * 0.6 + avg_rt_score * 0.4
    return int(efficiency)


def calculate_score(answers: List[Dict], game_type: str) -> tuple:
    """
    计算筛查评分，返回 (总分, 各维度分数列表)。

    总分 = 效率分（正确率 60% + 反应时 40%）。
    注意力维度：用反应时稳定性（变异系数）单独估算，
    变异系数越低（答题节奏越稳定）→ 注意力得分越高。
    """
    if not answers:
        return 0, []

    total_score = _calc_efficiency_score(answers)

    # 游戏类型 → 能力维度映射
    dimension_map = {
        "visual": ["visual_discrimination", "attention"],
        "spelling": ["spelling", "phonological", "character_order"],
        "comprehension": ["reading_comprehension", "semantic_integration", "information_extraction"]
    }
    dimensions = dimension_map.get(game_type, ["general"])

    dimension_scores = []
    for dim in dimensions:
        if dim == "attention":
            # 用反应时变异系数估算注意力：CV = std / mean，CV 越小越专注
            times = [a.get("time_spent", 0) for a in answers if a.get("time_spent") and not a.get("is_timeout")]
            if len(times) >= 3:
                mean_t = sum(times) / len(times)
                variance = sum((t - mean_t) ** 2 for t in times) / len(times)
                std_t = variance ** 0.5
                cv = std_t / mean_t if mean_t > 0 else 1.0
                # CV=0 → 100分；CV=1.0 → 0分；线性映射
                attention_score = max(0, int((1.0 - min(cv, 1.0)) * 100))
            else:
                attention_score = total_score
            dimension_scores.append({"dimension": dim, "score": attention_score})
        else:
            dimension_scores.append({"dimension": dim, "score": total_score})

    return total_score, dimension_scores


def determine_risk_level(scores: Dict[str, int], efficiency_score: int = None) -> str:
    """
    风险判定：综合维度得分均值 + 效率分（正确率/反应时）。

    - efficiency_score 直接传入时优先使用；否则从 scores 均值推算。
    - 任意维度 < 50 → 直接高风险（单维度严重缺陷）
    - 均值 ≥ 75 且无弱项 → 低风险
    - 均值 ≥ 60 或弱项 ≤ 1 → 中风险
    - 其余 → 高风险
    """
    if not scores:
        return "medium"

    base_score = efficiency_score if efficiency_score is not None else sum(scores.values()) / len(scores)
    avg_score = sum(scores.values()) / len(scores)

    # 单维度严重缺陷（< 50）直接高风险
    critical_dims = [k for k, v in scores.items() if v < 50]
    if critical_dims:
        return "high"

    low_dims = [k for k, v in scores.items() if v < 60]

    # 效率分和维度均值都达标才算低风险
    if base_score >= 75 and avg_score >= 75 and len(low_dims) == 0:
        return "low"
    elif base_score >= 60 or (avg_score >= 60 and len(low_dims) <= 1):
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
