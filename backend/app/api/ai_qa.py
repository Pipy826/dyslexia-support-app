from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from ..database import get_db
from ..models.ai_chat import AIConversation, SavedMessage
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
        # 验证 child 归属当前用户
        from ..models.child import Child
        child = db.query(Child).filter(
            Child.id == data.child_id,
            Child.parent_id == current_user.id
        ).first()
        if child:
            report = db.query(Report).filter(
                Report.child_id == data.child_id
            ).order_by(Report.created_at.desc()).first()

            if report:
                context["risk_level"] = report.risk_level
                if report.dimensions:
                    context["dimensions"] = json.loads(report.dimensions)

    # 获取最近对话历史传给 LLM（最多20条）
    history_records = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id,
        AIConversation.child_id == data.child_id
    ).order_by(AIConversation.created_at.desc()).limit(20).all()
    history = [{"role": h.role, "message": h.message} for h in reversed(history_records)]

    # Get AI response (LLM if configured, else rule-based)
    reply = await get_ai_response(data.message, context, history)

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


@router.post("/save/{message_id}")
def save_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """收藏一条 AI 回复"""
    msg = db.query(AIConversation).filter(
        AIConversation.id == message_id,
        AIConversation.user_id == current_user.id,
        AIConversation.role == "assistant"
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")

    # 避免重复收藏
    existing = db.query(SavedMessage).filter(
        SavedMessage.user_id == current_user.id,
        SavedMessage.conversation_id == message_id
    ).first()
    if existing:
        return {"id": existing.id, "already_saved": True}

    saved = SavedMessage(
        user_id=current_user.id,
        child_id=msg.child_id,
        conversation_id=message_id,
        content=msg.message
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"id": saved.id, "already_saved": False}


@router.delete("/save/{message_id}")
def unsave_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消收藏"""
    saved = db.query(SavedMessage).filter(
        SavedMessage.user_id == current_user.id,
        SavedMessage.conversation_id == message_id
    ).first()
    if saved:
        db.delete(saved)
        db.commit()
    return {"message": "已取消收藏"}


@router.get("/saved")
def get_saved_messages(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收藏的消息列表"""
    query = db.query(SavedMessage).filter(SavedMessage.user_id == current_user.id)
    if child_id:
        query = query.filter(SavedMessage.child_id == child_id)
    items = query.order_by(SavedMessage.created_at.desc()).all()
    return [
        {"id": i.id, "conversation_id": i.conversation_id, "content": i.content, "created_at": i.created_at}
        for i in items
    ]
