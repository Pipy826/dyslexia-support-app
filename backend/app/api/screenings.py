from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from ..database import get_db
from ..models.screening import Screening, Report
from ..models.child import Child
from ..schemas.screening import (
    ScreeningStart, ScreeningSubmit, ScreeningResponse,
    GameQuestionsResponse, QuestionOption
)
from ..services.screening_service import create_screening_report
from ..games import VISUAL_QUESTIONS, SPELLING_QUESTIONS, COMPREHENSION_QUESTIONS
from .deps import get_current_user
from ..models.user import User

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

    # Return requested count of questions
    selected = level_questions[:count]

    # Remove correct_index from response (don't expose answer to frontend)
    questions_for_client = []
    for q in selected:
        q_copy = {k: v for k, v in q.items() if k != "correct_index"}
        questions_for_client.append(q_copy)

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
def submit_screening(
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
            "time_spent": answer.time_spent
        })

    # Store behavior data
    if data.behavior_data:
        screening.behavior_data = json.dumps(data.behavior_data, ensure_ascii=False)

    # Create report
    report = create_screening_report(
        db=db,
        child_id=screening.child_id,
        screening_id=screening.id,
        game_type=screening.game_type,
        answers=graded_answers
    )

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
