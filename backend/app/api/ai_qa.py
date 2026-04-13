from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from ..database import get_db
from ..models.ai_chat import AIConversation
from ..models.screening import Report
from ..models.child import Child
from ..schemas.ai_chat import AIChatRequest, AIChatResponse
from ..services.ai_service import get_ai_response
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/ai", tags=["AI问答"])


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    data: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message and get AI response"""
    # Save user message
    user_msg = AIConversation(
        user_id=current_user.id,
        child_id=data.child_id,
        role="user",
        message=data.message
    )
    db.add(user_msg)
    db.commit()

    # Get context if child_id provided
    context = {}
    if data.child_id:
        report = db.query(Report).filter(
            Report.child_id == data.child_id
        ).order_by(Report.created_at.desc()).first()

        if report:
            context["risk_level"] = report.risk_level
            if report.dimensions:
                context["dimensions"] = json.loads(report.dimensions)

    # Get AI response (LLM if configured, else rule-based)
    reply = await get_ai_response(data.message, context)

    # Save assistant message
    assistant_msg = AIConversation(
        user_id=current_user.id,
        child_id=data.child_id,
        role="assistant",
        message=reply
    )
    db.add(assistant_msg)
    db.commit()

    return AIChatResponse(
        reply=reply,
        conversation_id=assistant_msg.id
    )


@router.get("/history", response_model=List[dict])
def get_chat_history(
    child_id: int = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat history"""
    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    )

    if child_id:
        query = query.filter(AIConversation.child_id == child_id)

    messages = query.order_by(AIConversation.created_at.desc()).limit(limit).all()

    # Reverse to show oldest first
    messages = list(reversed(messages))

    return [
        {
            "id": m.id,
            "role": m.role,
            "message": m.message,
            "created_at": m.created_at
        }
        for m in messages
    ]


@router.delete("/history")
def clear_chat_history(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear chat history"""
    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    )

    if child_id:
        query = query.filter(AIConversation.child_id == child_id)

    query.delete()
    db.commit()

    return {"message": "Chat history cleared"}
