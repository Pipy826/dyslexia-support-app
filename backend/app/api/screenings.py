from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
import json

from ..database import get_db
from ..models.screening import Screening, Report
from ..models.child import Child
from ..models.training import TrainingTask
from ..schemas.screening import (
    ScreeningStart, ScreeningSubmit, ScreeningResponse,
    GameQuestionsResponse, QuestionOption
)
from ..services.screening_service import create_screening_report_async
from ..games import VISUAL_QUESTIONS, SPELLING_QUESTIONS, COMPREHENSION_QUESTIONS
from .deps import get_current_user
from ..models.user import User

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
    today = date.today()
    # 检查今天是否已有任务
    existing = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id,
        TrainingTask.scheduled_date == today
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
            scheduled_date=today,
            status="pending"
        )
        db.add(task)
    db.commit()

router = APIRouter(prefix="/api/screenings", tags=["筛查"])


GAME_QUESTIONS = {
    "visual": VISUAL_QUESTIONS,
    "spelling": SPELLING_QUESTIONS,
    "comprehension": COMPREHENSION_QUESTIONS
}


@router.get("/questions/{game_type}")
def get_questions(
    game_type: str,
    difficulty: str = "L1",
    count: int = 10
):
    """Get game questions by type and difficulty"""
    if game_type not in GAME_QUESTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid game type. Must be one of: {list(GAME_QUESTIONS.keys())}"
        )

    questions_db = GAME_QUESTIONS.get(game_type, {})
    level_questions = questions_db.get(difficulty, [])

    # 取指定数量，包含 correct_index 供前端即时反馈
    questions_for_client = list(level_questions[:count])

    return {
        "questions": questions_for_client,
        "game_type": game_type,
        "difficulty": difficulty
    }


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
            "is_timeout": answer.is_timeout
        })

    # 将行为数据（含每题细节）存入 behavior_data
    behavior_payload = {
        "answers_detail": graded_answers,
        **(data.behavior_data or {})
    }
    screening.behavior_data = json.dumps(behavior_payload, ensure_ascii=False)

    # Create report (async, AI runs in background to avoid blocking response)
    import asyncio
    from ..services.screening_service import calculate_score, determine_risk_level, generate_summary, generate_recommendations

    # 先用模板快速生成报告，保证前端能立即拿到结果
    total_score, dimension_scores = calculate_score(graded_answers, screening.game_type)
    scores_dict = {ds["dimension"]: ds["score"] for ds in dimension_scores}
    risk_level = determine_risk_level(scores_dict)

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

    # 后台异步用 AI 更新 summary（不阻塞响应）
    async def _update_summary_async(report_id: int, child_name: str, age: int):
        from ..database import SessionLocal
        from ..services.ai_service import generate_report_interpretation
        try:
            ai_summary = await generate_report_interpretation(
                child_name=child_name,
                child_age=age,
                risk_level=risk_level,
                overall_score=total_score,
                dimensions=scores_dict,
            )
            bg_db = SessionLocal()
            try:
                bg_report = bg_db.query(Report).filter(Report.id == report_id).first()
                if bg_report:
                    bg_report.summary = ai_summary
                    bg_db.commit()
            finally:
                bg_db.close()
        except Exception:
            pass  # AI 失败不影响主流程

    today_date = datetime.now().date()
    age = today_date.year - child.birth_date.year - (
        (today_date.month, today_date.day) < (child.birth_date.month, child.birth_date.day)
    )
    asyncio.create_task(_update_summary_async(report.id, child.name, age))

    # 根据报告结果自动生成今日训练任务
    scores_dict = json.loads(report.dimensions) if report.dimensions else {}
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
