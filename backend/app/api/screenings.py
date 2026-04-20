from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
import json
import logging

from ..database import get_db
from ..models.screening import Screening, Report
from ..models.child import Child
from ..models.training import TrainingTask
from ..schemas.screening import (
    ScreeningStart, ScreeningSubmit, ScreeningResponse,
    GameQuestionsResponse, QuestionOption
)
from ..games import (
    VISUAL_QUESTIONS, SPELLING_QUESTIONS, COMPREHENSION_QUESTIONS,
    SORT_ORDER_QUESTIONS,
    WORKING_MEMORY_QUESTIONS, RAPID_NAMING_QUESTIONS, MOTOR_COORDINATION_QUESTIONS,
)
from .deps import get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)

# 根据风险等级和弱项维度自动推荐训练任务
TASK_TEMPLATES = {
    "visual_discrimination": {"task_type": "visual", "task_name": "火眼金睛（视觉辨识训练）"},
    "attention":             {"task_type": "visual", "task_name": "专注力训练"},
    "phonological":          {"task_type": "spelling", "task_name": "音形对应练习"},
    "character_order":       {"task_type": "spelling", "task_name": "字序组织训练"},
    "spelling":              {"task_type": "spelling", "task_name": "拼字小达人"},
    "reading_comprehension": {"task_type": "comprehension", "task_name": "阅读理解练习"},
    "semantic_integration":  {"task_type": "comprehension", "task_name": "语义整合训练"},
    "information_extraction":{"task_type": "comprehension", "task_name": "信息提取练习"},
    "working_memory_capacity":{"task_type": "working_memory", "task_name": "工作记忆强化训练"},
    "short_term_memory":     {"task_type": "working_memory", "task_name": "短时记忆练习"},
    "rapid_naming_speed":    {"task_type": "rapid_naming", "task_name": "快速命名训练"},
    "phonological_awareness":{"task_type": "rapid_naming", "task_name": "音韵意识练习"},
    "fine_motor_control":    {"task_type": "motor_coordination", "task_name": "精细动作训练"},
    "visual_motor_integration":{"task_type": "motor_coordination", "task_name": "视动整合练习"},
}

# 合法的 task_type 集合（前端传入时做校验）
VALID_TASK_TYPES = {
    "visual", "spelling", "comprehension", "working_memory",
    "rapid_naming", "motor_coordination",
}

DEFAULT_TASKS_BY_RISK = {
    "low": [
        {"task_type": "visual",        "task_name": "每日视觉热身"},
        {"task_type": "spelling",      "task_name": "拼字小达人"},
        {"task_type": "comprehension", "task_name": "亲子共读打卡"},
    ],
    "medium": [
        {"task_type": "visual",        "task_name": "火眼金睛（视觉辨识训练）"},
        {"task_type": "spelling",      "task_name": "音形对应练习"},
        {"task_type": "comprehension", "task_name": "阅读理解练习"},
    ],
    "high": [
        {"task_type": "visual",        "task_name": "视觉辨识强化训练"},
        {"task_type": "spelling",      "task_name": "字序组织训练"},
        {"task_type": "comprehension", "task_name": "语义整合训练"},
    ],
}

def _auto_create_training_tasks(db: Session, child_id: int, risk_level: str, scores_dict: dict):
    """根据报告结果自动创建今日训练任务（避免重复）"""
    from sqlalchemy import func
    # 使用 UTC 日期，与 created_at（utcnow）保持一致，避免时区偏差
    from datetime import timezone
    today_utc = datetime.utcnow().date()
    # 检查今天（UTC）是否已有任务
    existing = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id,
        TrainingTask.scheduled_date == today_utc,
    ).count()
    if existing > 0:
        return

    # 找出弱项维度（得分 < 70）
    weak_dims = [dim for dim, score in scores_dict.items() if score < 70]

    tasks_to_create = []
    seen_types = set()

    # 优先为弱项维度创建任务
    for dim in weak_dims:
        tmpl = TASK_TEMPLATES.get(dim)
        if tmpl and tmpl["task_type"] not in seen_types:
            tasks_to_create.append(tmpl)
            seen_types.add(tmpl["task_type"])
        if len(tasks_to_create) >= 3:
            break

    # 不足3个时用默认任务补齐
    if len(tasks_to_create) < 3:
        for tmpl in DEFAULT_TASKS_BY_RISK.get(risk_level, DEFAULT_TASKS_BY_RISK["medium"]):
            if tmpl["task_type"] not in seen_types:
                tasks_to_create.append(tmpl)
                seen_types.add(tmpl["task_type"])
            if len(tasks_to_create) >= 3:
                break

    for tmpl in tasks_to_create:
        task = TrainingTask(
            child_id=child_id,
            task_type=tmpl["task_type"],
            task_name=tmpl["task_name"],
            scheduled_date=today_utc,
            status="pending"
        )
        db.add(task)
    db.commit()

router = APIRouter(prefix="/api/screenings", tags=["筛查"])


GAME_QUESTIONS = {
    "visual": VISUAL_QUESTIONS,
    "spelling": SPELLING_QUESTIONS,
    "comprehension": COMPREHENSION_QUESTIONS,
    "sort_order": SORT_ORDER_QUESTIONS,   # 拖拽排序题（文字理解子类型）
    "working_memory": WORKING_MEMORY_QUESTIONS,
    "rapid_naming": RAPID_NAMING_QUESTIONS,
    "motor_coordination": MOTOR_COORDINATION_QUESTIONS,
}

# 学龄 → 难度等级 + 时限补偿系数映射
# time_multiplier: 在题目原始 time_limit 基础上乘以该系数
# allowed_game_types: 该学龄段推荐的游戏类型列表
# excluded_question_types: 该学龄段需要过滤掉的题目 type 值列表
GRADE_DIFFICULTY_MAP = {
    # 学龄前 / 幼儿园
    "preschool":  {
        "difficulty": "L1",
        "time_multiplier": 1.5,
        "allowed_game_types": ["visual", "working_memory", "motor_coordination"],
        "excluded_question_types": ["spelling_recognition"],
    },
    "幼儿园":      {
        "difficulty": "L1",
        "time_multiplier": 1.5,
        "allowed_game_types": ["visual", "working_memory", "motor_coordination"],
        "excluded_question_types": ["spelling_recognition"],
    },
    "学前":        {
        "difficulty": "L1",
        "time_multiplier": 1.5,
        "allowed_game_types": ["visual", "working_memory", "motor_coordination"],
        "excluded_question_types": ["spelling_recognition"],
    },
    # 1-2 年级
    "grade_1":    {
        "difficulty": "L1",
        "time_multiplier": 1.2,
        "allowed_game_types": ["visual", "spelling", "comprehension", "rapid_naming"],
        "excluded_question_types": [],
    },
    "grade_2":    {
        "difficulty": "L1",
        "time_multiplier": 1.2,
        "allowed_game_types": ["visual", "spelling", "comprehension", "rapid_naming"],
        "excluded_question_types": [],
    },
    "一年级":      {
        "difficulty": "L1",
        "time_multiplier": 1.2,
        "allowed_game_types": ["visual", "spelling", "comprehension", "rapid_naming"],
        "excluded_question_types": [],
    },
    "二年级":      {
        "difficulty": "L1",
        "time_multiplier": 1.2,
        "allowed_game_types": ["visual", "spelling", "comprehension", "rapid_naming"],
        "excluded_question_types": [],
    },
    # 3-4 年级
    "grade_3":    {
        "difficulty": "L2",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    "grade_4":    {
        "difficulty": "L2",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    "三年级":      {
        "difficulty": "L2",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    "四年级":      {
        "difficulty": "L2",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    # 5-6 年级
    "grade_5":    {
        "difficulty": "L3",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    "grade_6":    {
        "difficulty": "L3",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    "五年级":      {
        "difficulty": "L3",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
    "六年级":      {
        "difficulty": "L3",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": [],
    },
}

# 未匹配到 grade 时的默认值
_DEFAULT_GRADE_CONFIG = {
    "difficulty": "L1",
    "time_multiplier": 1.0,
    "allowed_game_types": [],
    "excluded_question_types": [],
}


def _resolve_difficulty(grade: str | None, explicit_difficulty: str | None) -> tuple[str, float, list]:
    """
    返回 (difficulty, time_multiplier, excluded_question_types)。
    优先级：显式传入的 difficulty > grade 映射 > 默认值。
    注意：即使显式传入 difficulty，仍然应用 grade 对应的 time_multiplier 和 excluded_question_types。
    """
    if grade:
        cfg = GRADE_DIFFICULTY_MAP.get(grade.strip(), _DEFAULT_GRADE_CONFIG)
        difficulty = explicit_difficulty if explicit_difficulty else cfg["difficulty"]
        return difficulty, cfg["time_multiplier"], cfg.get("excluded_question_types", [])
    if explicit_difficulty:
        return explicit_difficulty, 1.0, []
    return _DEFAULT_GRADE_CONFIG["difficulty"], _DEFAULT_GRADE_CONFIG["time_multiplier"], []


@router.get("/questions/{game_type}")
def get_questions(
    game_type: str,
    difficulty: str = None,
    grade: str = None,
    count: int = 10
):
    """
    获取游戏题目。

    难度解析优先级：
    1. 显式传入 difficulty（自适应调难时使用）
    2. 根据 grade 自动映射（首次加载时使用）
    3. 默认 L1

    学龄前孩子的 time_limit 会自动乘以 1.5 倍补偿系数。
    """
    if game_type not in GAME_QUESTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的游戏类型，可选：{list(GAME_QUESTIONS.keys())}"
        )

    resolved_difficulty, time_multiplier, excluded_question_types = _resolve_difficulty(grade, difficulty)

    questions_db = GAME_QUESTIONS.get(game_type, {})
    level_questions = questions_db.get(resolved_difficulty, [])

    # 按学龄段过滤不适龄题型（如学龄前过滤拼音题）
    if excluded_question_types:
        level_questions = [q for q in level_questions if q.get("type") not in excluded_question_types]

    # 取指定数量，包含 correct_index 供前端即时反馈
    # 学龄前补偿：time_limit 乘以系数并取整
    available_count = len(level_questions)
    questions_for_client = []
    for q in level_questions[:count]:
        if time_multiplier != 1.0:
            q = dict(q)  # 浅拷贝，不修改原始题库
            q["time_limit"] = round(q.get("time_limit", 10) * time_multiplier)
        questions_for_client.append(q)

    response = {
        "questions": questions_for_client,
        "game_type": game_type,
        "difficulty": resolved_difficulty,
        "grade": grade,
        "time_multiplier": time_multiplier,
    }
    # 仅当过滤后题目不足 count 时才附加 available_count（向后兼容）
    if available_count < count:
        response["available_count"] = available_count
    return response


@router.post("/start", response_model=ScreeningResponse)
def start_screening(
    data: ScreeningStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new screening"""
    # Verify child belongs to user
    child = db.query(Child).filter(
        Child.id == data.child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    # Create screening record
    screening = Screening(
        child_id=data.child_id,
        game_type=data.game_type,
        score=0,
        started_at=datetime.utcnow()
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)

    return ScreeningResponse.model_validate(screening)


@router.post("/submit")
async def submit_screening(
    data: ScreeningSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit screening answers and get results"""
    # Get screening
    screening = db.query(Screening).filter(Screening.id == data.screening_id).first()

    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening not found"
        )

    # 防止重复提交：已完成的筛查直接返回已有报告
    if screening.completed_at is not None:
        existing_report = db.query(Report).filter(
            Report.screening_id == screening.id
        ).first()
        if existing_report:
            return {
                "screening_id": screening.id,
                "report_id": existing_report.id,
                "score": existing_report.overall_score,
                "risk_level": existing_report.risk_level,
                "summary": existing_report.summary
            }

    # Verify child belongs to user
    child = db.query(Child).filter(
        Child.id == screening.child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Process answers - need to get correct answers to grade
    questions_db = GAME_QUESTIONS.get(screening.game_type, {})
    all_questions = []
    for level_qs in questions_db.values():
        all_questions.extend(level_qs)

    question_map = {q["id"]: q for q in all_questions}

    # Grade answers
    graded_answers = []
    for answer in data.answers:
        q = question_map.get(answer.question_id, {})
        correct_idx = q.get("correct_index", -1)
        is_correct = answer.answer == correct_idx

        graded_answers.append({
            "question_id": answer.question_id,
            "answer": answer.answer,
            "correct_index": correct_idx,
            "is_correct": is_correct,
            "time_spent": answer.time_spent,
            "reaction_time": answer.reaction_time,
            "change_count": answer.change_count,
            "is_timeout": answer.is_timeout,
            "time_limit": q.get("time_limit", 10),   # 保留题目原始时限，供效率分计算使用
        })

    # 将行为数据（含每题细节）存入 behavior_data
    behavior_payload = {
        "answers_detail": graded_answers,
        **(data.behavior_data or {})
    }
    screening.behavior_data = json.dumps(behavior_payload, ensure_ascii=False)

    from ..services.screening_service import calculate_score, determine_risk_level, generate_summary, generate_recommendations

    # 先用模板快速生成报告，保证前端能立即拿到结果
    total_score, dimension_scores = calculate_score(graded_answers, screening.game_type)
    scores_dict = {ds["dimension"]: ds["score"] for ds in dimension_scores}
    risk_level = determine_risk_level(scores_dict, efficiency_score=total_score)

    from ..models.screening import DimensionScore
    for ds in dimension_scores:
        db.add(DimensionScore(
            screening_id=screening.id,
            dimension=ds["dimension"],
            score=ds["score"],
        ))

    screening.score = total_score
    screening.risk_level = risk_level
    screening.completed_at = datetime.utcnow()

    summary = generate_summary(child.name, 0, risk_level, scores_dict)
    recommendations = generate_recommendations(risk_level, scores_dict)

    from ..models.screening import Report
    report = Report(
        child_id=screening.child_id,
        screening_id=screening.id,
        overall_score=total_score,
        risk_level=risk_level,
        summary=summary,
        recommendations=recommendations,
        dimensions=json.dumps(scores_dict, ensure_ascii=False),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # 计算孩子年龄（统一使用 UTC 日期，与数据库保持一致）
    today_date = datetime.utcnow().date()
    age = today_date.year - child.birth_date.year - (
        (today_date.month, today_date.day) < (child.birth_date.month, child.birth_date.day)
    )

    # 后台用 AI 更新 summary（BackgroundTasks 比 asyncio.create_task 更安全可靠）
    async def _update_summary_async(
        report_id: int,
        child_name: str,
        child_age: int,
        _risk_level: str,
        _total_score: int,
        _scores_dict: dict,
    ):
        from ..database import SessionLocal
        from ..services.ai_service import generate_report_interpretation
        try:
            ai_summary = await generate_report_interpretation(
                child_name=child_name,
                child_age=child_age,
                risk_level=_risk_level,
                overall_score=_total_score,
                dimensions=_scores_dict,
            )
            bg_db = SessionLocal()
            try:
                bg_report = bg_db.query(Report).filter(Report.id == report_id).first()
                if bg_report:
                    bg_report.summary = ai_summary
                    bg_db.commit()
            finally:
                bg_db.close()
        except Exception as e:
            logger.warning(f"AI summary update failed for report {report_id}: {e}")

    background_tasks.add_task(
        _update_summary_async,
        report.id, child.name, age,
        risk_level, total_score, scores_dict,
    )

    # 根据报告结果自动生成今日训练任务
    _auto_create_training_tasks(db, screening.child_id, report.risk_level, scores_dict)

    return {
        "screening_id": screening.id,
        "report_id": report.id,
        "score": report.overall_score,
        "risk_level": report.risk_level,
        "summary": report.summary
    }


@router.get("/history", response_model=List[ScreeningResponse])
def get_screening_history(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get screening history for user's children"""
    query = db.query(Screening).join(Child).filter(Child.parent_id == current_user.id)

    if child_id:
        query = query.filter(Screening.child_id == child_id)

    screenings = query.order_by(Screening.created_at.desc()).all()
    return [ScreeningResponse.model_validate(s) for s in screenings]
