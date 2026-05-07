from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models.screening import Report
from ..models.child import Child
from ..schemas.report import ReportResponse
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/reports", tags=["报告"])


@router.get("/game-activity/{child_id}")
def get_game_activity_report(
    child_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取孩子的游戏活动情况报告（家长端使用）。
    包含：
    - 总体游戏统计（总次数、总时长、平均正确率）
    - 各游戏类型的详细统计
    - 近期游戏记录（最近20条）
    - 进步趋势（近7天 vs 前7天正确率对比）
    - 连续打卡天数
    """
    import json
    from ..models.training import TrainingTask, CheckInRecord
    from sqlalchemy import func

    # 验证孩子归属
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    days = max(7, min(days, 90))
    since_date = datetime.utcnow() - timedelta(days=days)

    # 查询该时间段内已完成的训练任务
    tasks = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id,
        TrainingTask.status == "completed",
        TrainingTask.completed_at >= since_date
    ).order_by(TrainingTask.completed_at.desc()).all()

    # 游戏类型中文名
    GAME_TYPE_NAMES = {
        "visual": "视觉辨识", "spelling": "拼字识别", "comprehension": "文字理解",
        "working_memory": "工作记忆", "rapid_naming": "快速命名",
        "motor_coordination": "精细动作", "handwriting": "汉字书写",
        "flip_card": "翻牌记忆", "connect_game": "连一连",
    }
    GAME_TYPE_ICONS = {
        "visual": "ph-eye", "spelling": "ph-text-aa", "comprehension": "ph-book-open",
        "working_memory": "ph-brain", "rapid_naming": "ph-lightning",
        "motor_coordination": "ph-hand", "handwriting": "ph-pencil-line",
        "flip_card": "ph-cards", "connect_game": "ph-link",
    }
    GAME_TYPE_COLORS = {
        "visual": "#4F9EF8", "spelling": "#A78BFA", "comprehension": "#22C55E",
        "working_memory": "#F97316", "rapid_naming": "#EAB308",
        "motor_coordination": "#EC4899", "handwriting": "#F57F17",
        "flip_card": "#7C3AED", "connect_game": "#16A34A",
    }

    # 按游戏类型分组统计
    game_stats: dict = {}
    for task in tasks:
        gt = task.task_type
        if gt not in game_stats:
            game_stats[gt] = {
                "game_type": gt,
                "game_name": GAME_TYPE_NAMES.get(gt, gt),
                "icon": GAME_TYPE_ICONS.get(gt, "ph-star"),
                "color": GAME_TYPE_COLORS.get(gt, "#4F9EF8"),
                "play_count": 0,
                "total_correct": 0,
                "total_questions": 0,
                "accuracy_sum": 0,
                "accuracy_count": 0,
                "last_played": None,
            }
        s = game_stats[gt]
        s["play_count"] += 1
        if task.correct_count is not None:
            s["total_correct"] += task.correct_count
        if task.total_count is not None:
            s["total_questions"] += task.total_count
        if task.accuracy is not None:
            s["accuracy_sum"] += task.accuracy
            s["accuracy_count"] += 1
        if task.completed_at:
            if s["last_played"] is None or task.completed_at > s["last_played"]:
                s["last_played"] = task.completed_at

    # 计算各游戏类型平均正确率
    game_stats_list = []
    for gt, s in game_stats.items():
        avg_accuracy = round(s["accuracy_sum"] / s["accuracy_count"]) if s["accuracy_count"] > 0 else None
        game_stats_list.append({
            "game_type": s["game_type"],
            "game_name": s["game_name"],
            "icon": s["icon"],
            "color": s["color"],
            "play_count": s["play_count"],
            "total_correct": s["total_correct"],
            "total_questions": s["total_questions"],
            "avg_accuracy": avg_accuracy,
            "last_played": s["last_played"].isoformat() if s["last_played"] else None,
        })
    # 按游戏次数降序排列
    game_stats_list.sort(key=lambda x: x["play_count"], reverse=True)

    # 总体统计
    total_plays = len(tasks)
    all_accuracies = [t.accuracy for t in tasks if t.accuracy is not None]
    overall_accuracy = round(sum(all_accuracies) / len(all_accuracies)) if all_accuracies else None
    total_correct = sum(t.correct_count or 0 for t in tasks)
    total_questions = sum(t.total_count or 0 for t in tasks)

    # 近期游戏记录（最近20条）
    recent_records = []
    for task in tasks[:20]:
        extra = {}
        if task.extra_data:
            try:
                extra = json.loads(task.extra_data)
            except Exception:
                pass
        recent_records.append({
            "id": task.id,
            "game_type": task.task_type,
            "game_name": GAME_TYPE_NAMES.get(task.task_type, task.task_type),
            "icon": GAME_TYPE_ICONS.get(task.task_type, "ph-star"),
            "color": GAME_TYPE_COLORS.get(task.task_type, "#4F9EF8"),
            "correct_count": task.correct_count,
            "total_count": task.total_count,
            "accuracy": task.accuracy,
            "stars": extra.get("stars_earned", extra.get("stars", None)),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        })

    # 进步趋势：近7天 vs 前7天正确率对比
    now = datetime.utcnow()
    week1_start = now - timedelta(days=7)
    week2_start = now - timedelta(days=14)

    recent_7_tasks = [t for t in tasks if t.completed_at and t.completed_at >= week1_start]
    prev_7_tasks = [t for t in tasks if t.completed_at and week2_start <= t.completed_at < week1_start]

    recent_7_acc = [t.accuracy for t in recent_7_tasks if t.accuracy is not None]
    prev_7_acc = [t.accuracy for t in prev_7_tasks if t.accuracy is not None]

    recent_avg = round(sum(recent_7_acc) / len(recent_7_acc)) if recent_7_acc else None
    prev_avg = round(sum(prev_7_acc) / len(prev_7_acc)) if prev_7_acc else None

    trend = None
    trend_delta = None
    if recent_avg is not None and prev_avg is not None:
        trend_delta = recent_avg - prev_avg
        trend = "up" if trend_delta > 2 else ("down" if trend_delta < -2 else "flat")
    elif recent_avg is not None:
        trend = "new"

    # 连续打卡天数
    today = date.today()
    latest_checkin = db.query(CheckInRecord).filter(
        CheckInRecord.child_id == child_id
    ).order_by(CheckInRecord.check_in_date.desc()).first()
    current_streak = latest_checkin.streak_count if latest_checkin else 0

    # 近30天每日游戏次数（用于日历热力图）
    daily_counts: dict = {}
    all_tasks_30d = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id,
        TrainingTask.status == "completed",
        TrainingTask.completed_at >= now - timedelta(days=30)
    ).all()
    for task in all_tasks_30d:
        if task.completed_at:
            day_str = task.completed_at.strftime("%Y-%m-%d")
            daily_counts[day_str] = daily_counts.get(day_str, 0) + 1

    return {
        "child_id": child_id,
        "child_name": child.name,
        "period_days": days,
        "summary": {
            "total_plays": total_plays,
            "overall_accuracy": overall_accuracy,
            "total_correct": total_correct,
            "total_questions": total_questions,
            "current_streak": current_streak,
            "games_played_types": len(game_stats),
        },
        "trend": {
            "direction": trend,
            "delta": trend_delta,
            "recent_7_avg": recent_avg,
            "prev_7_avg": prev_avg,
        },
        "game_stats": game_stats_list,
        "recent_records": recent_records,
        "daily_counts": daily_counts,
    }


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    child_id: int = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reports for user's children, with game_type attached"""
    from ..models.screening import Screening
    import json as _json

    # 参数范围校验
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    query = db.query(Report).join(Child).filter(Child.parent_id == current_user.id)
    if child_id:
        query = query.filter(Report.child_id == child_id)

    reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()

    # 批量查询关联的 Screening，避免 N+1
    screening_ids = [r.screening_id for r in reports if r.screening_id]
    screenings = {
        s.id: s for s in db.query(Screening).filter(Screening.id.in_(screening_ids)).all()
    } if screening_ids else {}

    results = []
    for r in reports:
        item = ReportResponse.model_validate(r)
        sc = screenings.get(r.screening_id)
        if sc:
            item.game_type = sc.game_type
        results.append(item)
    return results


# ── 固定路径路由必须在参数路由之前注册，避免被 /{report_id} 误匹配 ──────────

@router.get("/by-screening/{screening_id}", response_model=ReportResponse)
def get_report_by_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report by screening_id"""
    report = db.query(Report).join(Child).filter(
        Report.screening_id == screening_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse.model_validate(report)


@router.get("/growth-diary/{child_id}")
def get_growth_diary(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取孩子的成长日记数据，包含：
    - 最新游戏的能力标签
    - 6维度星级（来自合并维度）
    - 近5次游戏的星级变化
    - AI 个性化观察文字
    - 推荐练习列表（基于最低分维度）
    """
    import json
    from ..models.screening import Screening

    # 1. 验证孩子归属
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    # 2. 查询最新报告
    latest_report = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.desc()).first()

    # 3. 构建合并维度（取每个游戏类型最新报告的分数）
    all_reports = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.asc()).all()

    merged_dimensions: dict = {}
    for report in all_reports:
        if not report.dimensions:
            continue
        try:
            dims = json.loads(report.dimensions)
        except (json.JSONDecodeError, TypeError):
            continue
        for dim, score in dims.items():
            if isinstance(score, (int, float)):
                merged_dimensions[dim] = int(score)

    # 将子维度映射到6个游戏类型维度
    GAME_TYPE_DIM_MAP = {
        "visual": ["visual_discrimination"],
        "spelling": ["phonological", "character_order", "spelling"],
        "comprehension": ["reading_comprehension", "semantic_integration", "information_extraction"],
        "working_memory": ["working_memory_capacity", "short_term_memory", "attention"],
        "rapid_naming": ["rapid_naming_speed", "phonological_awareness"],
        "motor_coordination": ["fine_motor_control", "visual_motor_integration"],
    }

    def get_game_type_score(game_type: str) -> int | None:
        """从合并维度中计算游戏类型的平均分"""
        dims = GAME_TYPE_DIM_MAP.get(game_type, [])
        scores = [merged_dimensions[d] for d in dims if d in merged_dimensions]
        if not scores:
            return None
        return int(sum(scores) / len(scores))

    # 构建6维度分数
    all_game_types = ["visual", "spelling", "comprehension", "working_memory", "rapid_naming", "motor_coordination"]
    dimensions_6 = {}
    for gt in all_game_types:
        # 优先从筛查记录直接取分数
        sc = db.query(Screening).filter(
            Screening.child_id == child_id,
            Screening.game_type == gt,
            Screening.completed_at.isnot(None)
        ).order_by(Screening.created_at.desc()).first()
        if sc:
            dimensions_6[gt] = sc.score
        else:
            computed = get_game_type_score(gt)
            if computed is not None:
                dimensions_6[gt] = computed

    # 4. 获取最新游戏的能力标签
    latest_ability = None
    if latest_report and latest_report.screening_id:
        latest_sc = db.query(Screening).filter(
            Screening.id == latest_report.screening_id
        ).first()
        if latest_sc:
            game_type = latest_sc.game_type
            score = latest_sc.score

            # 能力标签映射（与前端 abilityLabels.js 保持一致）
            ABILITY_LABELS = {
                "visual": {
                    "high": {"label": "眼力小达人", "emoji": "👁️", "desc": "你的眼睛很厉害，能快速找到不同！"},
                    "mid":  {"label": "眼力不错哦", "emoji": "😊", "desc": "再多练练，眼力会更强！"},
                    "low":  {"label": "眼力在成长", "emoji": "💪", "desc": "没关系，多玩几次就会进步！"},
                },
                "spelling": {
                    "high": {"label": "文字小魔法师", "emoji": "✨", "desc": "你认识好多字，真厉害！"},
                    "mid":  {"label": "文字小学徒",   "emoji": "📚", "desc": "继续加油，你会认识更多字！"},
                    "low":  {"label": "文字探险家",   "emoji": "🔍", "desc": "每个字都是新朋友，慢慢认识它们！"},
                },
                "comprehension": {
                    "high": {"label": "故事小达人",   "emoji": "📖", "desc": "你理解故事的能力超强！"},
                    "mid":  {"label": "故事小读者",   "emoji": "🌱", "desc": "多读故事，理解力会越来越好！"},
                    "low":  {"label": "故事小探索者", "emoji": "🗺️", "desc": "每个故事都有宝藏，慢慢发现！"},
                },
                "working_memory": {
                    "high": {"label": "记忆小冠军",   "emoji": "🧠", "desc": "你的记忆力超级棒！"},
                    "mid":  {"label": "记忆小能手",   "emoji": "💡", "desc": "记忆力不错，继续练习会更强！"},
                    "low":  {"label": "记忆小训练师", "emoji": "🎯", "desc": "记忆力是可以练出来的，加油！"},
                },
                "rapid_naming": {
                    "high": {"label": "反应小闪电", "emoji": "⚡", "desc": "你的反应速度超快！"},
                    "mid":  {"label": "反应小能手", "emoji": "🏃", "desc": "反应不错，多练练会更快！"},
                    "low":  {"label": "反应小学员", "emoji": "🌟", "desc": "慢慢来，速度会越来越快的！"},
                },
                "motor_coordination": {
                    "high": {"label": "手眼协调王",   "emoji": "🎯", "desc": "你的手眼配合超级棒！"},
                    "mid":  {"label": "手眼小能手",   "emoji": "✋", "desc": "配合不错，继续练习！"},
                    "low":  {"label": "手眼小训练师", "emoji": "💪", "desc": "多做手工游戏，会越来越好！"},
                },
            }

            level_key = "high" if score >= 75 else ("mid" if score >= 55 else "low")
            labels = ABILITY_LABELS.get(game_type, {})
            label_info = labels.get(level_key, {"label": "小小探险家", "emoji": "🌟", "desc": "你完成了挑战，真棒！"})

            latest_ability = {
                "game_type": game_type,
                "ability_label": label_info["label"],
                "ability_emoji": label_info["emoji"],
                "ability_desc": label_info["desc"],
                "score": score,
            }

    # 5. 查询近5次筛查记录，构建 score_history
    recent_screenings = db.query(Screening).filter(
        Screening.child_id == child_id,
        Screening.completed_at.isnot(None)
    ).order_by(Screening.created_at.desc()).limit(5).all()

    def score_to_stars(score: int) -> int:
        """score/20 取整，最小1最大5"""
        stars = max(1, min(5, int(score / 20)))
        return stars

    score_history = []
    for sc in reversed(recent_screenings):  # 按时间升序展示
        date_str = sc.created_at.strftime("%Y-%m-%d") if sc.created_at else ""
        score_history.append({
            "date": date_str,
            "score": sc.score,
            "stars": score_to_stars(sc.score),
            "game_type": sc.game_type,
        })

    # 6. 推荐游戏：从6维度中找出最低分的3个
    GAME_TYPE_NAMES = {
        "visual": "视觉辨识",
        "spelling": "拼字识别",
        "comprehension": "文字理解",
        "working_memory": "工作记忆",
        "rapid_naming": "快速命名",
        "motor_coordination": "精细动作",
    }
    GAME_TYPE_REASONS = {
        "visual": "视觉辨识能力需要加强",
        "spelling": "拼字识别需要加强",
        "comprehension": "文字理解需要加强",
        "working_memory": "工作记忆需要加强",
        "rapid_naming": "快速命名需要加强",
        "motor_coordination": "精细动作需要加强",
    }

    sorted_dims = sorted(dimensions_6.items(), key=lambda x: x[1])
    recommended_games = []
    for game_type, score in sorted_dims[:3]:
        recommended_games.append({
            "game_type": game_type,
            "game_name": GAME_TYPE_NAMES.get(game_type, game_type),
            "reason": GAME_TYPE_REASONS.get(game_type, f"{game_type}需要加强"),
        })

    # 如果维度不足3个，补充未完成的游戏类型
    completed_types = {item["game_type"] for item in recommended_games}
    for gt in all_game_types:
        if len(recommended_games) >= 3:
            break
        if gt not in completed_types and gt not in dimensions_6:
            recommended_games.append({
                "game_type": gt,
                "game_name": GAME_TYPE_NAMES.get(gt, gt),
                "reason": "还未探索过，快来试试！",
            })

    # 7. AI 观察文字（静态模板，基于最新报告数据）
    ai_observation = ""
    if latest_ability:
        child_name = child.name
        label = latest_ability["ability_label"]
        game_name = GAME_TYPE_NAMES.get(latest_ability["game_type"], "")
        score_val = latest_ability["score"]
        if score_val >= 75:
            ai_observation = f'{child_name}在{game_name}游戏中表现出色，获得了\u201c{label}\u201d称号！继续保持这种好状态，能力会越来越强的。'
        elif score_val >= 55:
            ai_observation = f'{child_name}在{game_name}游戏中表现不错，已经获得了\u201c{label}\u201d称号。再多练习几次，一定能更上一层楼！'
        else:
            ai_observation = f'{child_name}在{game_name}游戏中正在成长，获得了\u201c{label}\u201d称号。每一次练习都是进步，加油！'
    elif child:
        ai_observation = f"{child.name}还没有完成任何游戏，快去开始第一次冒险吧！"

    return {
        "child_id": child_id,
        "child_name": child.name,
        "latest_ability": latest_ability,
        "dimensions": dimensions_6,
        "score_history": score_history,
        "ai_observation": ai_observation,
        "recommended_games": recommended_games,
    }


@router.get("/child/{child_id}/merged-dimensions")
def get_merged_dimensions(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    合并该孩子所有筛查报告的维度得分。
    每个维度取最新一次筛查的得分，返回完整的多维度能力图谱。
    """
    import json

    # 验证孩子归属
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    # 按时间升序取所有报告（后面的会覆盖前面的，保证取最新值）
    reports = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.asc()).all()

    merged: dict = {}
    game_type_map: dict = {}  # dim -> game_type，用于标注来源

    from ..models.screening import Screening
    for report in reports:
        if not report.dimensions:
            continue
        try:
            dims = json.loads(report.dimensions)
        except (json.JSONDecodeError, TypeError):
            continue
        # 获取该报告对应的 game_type
        game_type = None
        if report.screening_id:
            sc = db.query(Screening).filter(Screening.id == report.screening_id).first()
            if sc:
                game_type = sc.game_type
        for dim, score in dims.items():
            if isinstance(score, (int, float)):
                merged[dim] = int(score)
                if game_type:
                    game_type_map[dim] = game_type

    # 统计已完成的游戏类型
    from ..models.screening import Screening as SC
    completed_game_types = [
        row[0] for row in db.query(SC.game_type).filter(
            SC.child_id == child_id,
            SC.completed_at.isnot(None)
        ).distinct().all()
    ]

    all_game_types = ["visual", "spelling", "comprehension", "working_memory", "rapid_naming", "motor_coordination"]
    pending_game_types = [g for g in all_game_types if g not in completed_game_types]

    return {
        "child_id": child_id,
        "child_name": child.name,
        "merged_dimensions": merged,
        "dimension_sources": game_type_map,
        "completed_game_types": completed_game_types,
        "pending_game_types": pending_game_types,
        "is_complete": len(pending_game_types) == 0,
    }


# ── 参数路由（必须在所有固定路径之后）────────────────────────────────────────

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific report"""
    from ..models.screening import Screening
    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # 附加 game_type（来自关联的 Screening）
    result = ReportResponse.model_validate(report)
    if report.screening_id:
        screening = db.query(Screening).filter(Screening.id == report.screening_id).first()
        if screening:
            result.game_type = screening.game_type
    return result


@router.get("/{report_id}/dimensions")
def get_report_dimensions(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed dimension scores for a report"""
    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    import json
    try:
        dimensions = json.loads(report.dimensions) if report.dimensions else {}
    except (json.JSONDecodeError, TypeError):
        dimensions = {}

    return {
        "report_id": report.id,
        "dimensions": dimensions,
        "overall_score": report.overall_score,
        "risk_level": report.risk_level
    }


@router.get("/{report_id}/export-text")
def export_report_text(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出报告为纯文字格式（服务端生成，前端直接展示或下载）。
    返回 JSON { content: "..." }，前端可复制到剪贴板或写入文件。
    """
    import json as _json
    from ..models.screening import Screening

    report = db.query(Report).join(Child).filter(
        Report.id == report_id,
        Child.parent_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    child = db.query(Child).filter(Child.id == report.child_id).first()
    child_name = child.name if child else "未知"

    # 获取 game_type
    game_type = "综合"
    game_type_names = {
        "visual": "视觉辨识", "spelling": "拼字识别", "comprehension": "文字理解",
        "working_memory": "工作记忆", "rapid_naming": "快速命名", "motor_coordination": "精细动作",
    }
    if report.screening_id:
        sc = db.query(Screening).filter(Screening.id == report.screening_id).first()
        if sc:
            game_type = game_type_names.get(sc.game_type, sc.game_type)

    risk_labels = {"low": "低风险", "medium": "中风险", "high": "高风险"}
    dim_names = {
        "visual_discrimination": "视觉辨识能力", "phonological": "音形映射能力",
        "character_order": "字序组织能力", "spelling": "拼写输出能力",
        "reading_comprehension": "阅读理解能力", "semantic_integration": "语义整合能力",
        "information_extraction": "信息提取能力", "attention": "任务注意力",
        "working_memory_capacity": "工作记忆容量", "short_term_memory": "短时记忆能力",
        "rapid_naming_speed": "快速命名速度", "phonological_awareness": "音韵意识",
        "fine_motor_control": "精细动作控制", "visual_motor_integration": "视动整合能力",
    }

    try:
        dimensions = _json.loads(report.dimensions) if report.dimensions else {}
    except Exception:
        dimensions = {}

    created_str = report.created_at.strftime("%Y-%m-%d") if report.created_at else ""

    lines = [
        "═══════════════════════════════",
        "  悦读灯塔 · 筛查评估报告",
        "═══════════════════════════════",
        f"孩子姓名：{child_name}",
        f"游戏类型：{game_type}",
        f"评估日期：{created_str}",
        f"综合得分：{report.overall_score} 分",
        f"风险等级：{risk_labels.get(report.risk_level, report.risk_level)}",
        "───────────────────────────────",
        "【评估总结】",
        report.summary or "暂无",
        "───────────────────────────────",
        "【各维度得分】",
    ]
    if dimensions:
        for dim, score in dimensions.items():
            bar = "█" * round(score / 10) + "░" * (10 - round(score / 10))
            name = dim_names.get(dim, dim).ljust(10)
            lines.append(f"{name}  {bar}  {score}分")
    else:
        lines.append("暂无维度数据")
    lines += [
        "───────────────────────────────",
        "【干预建议】",
        report.recommendations or "暂无",
        "───────────────────────────────",
        "⚠️ 本报告仅供参考，不构成医学诊断",
        "═══════════════════════════════",
    ]

    return {"content": "\n".join(lines), "child_name": child_name, "created_at": created_str}
