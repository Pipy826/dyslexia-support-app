"""
推送通知模块
- 存储设备推送 token（微信小程序 openid / H5 Web Push subscription）
- 提供通知记录的增删查接口
- 提供服务端主动推送接口（供定时任务或训练完成时调用）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db, Base
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/notifications", tags=["通知"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────

class PushToken(Base):
    """设备推送 token 表"""
    __tablename__ = "push_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(20), default="h5")   # h5 / mp-weixin / app
    token = Column(Text, nullable=False)           # Web Push subscription JSON / wx openid
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """通知记录表"""
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notif_type = Column(String(30), default="system")  # training_reminder / reassess / report / system
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    icon = Column(String(50), default="ph-bell")
    action = Column(String(50), default="")           # training / screening / report
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class PushTokenRegister(BaseModel):
    platform: str = "h5"
    token: str

class NotificationResponse(BaseModel):
    id: int
    notif_type: str
    title: str
    body: str
    icon: str
    action: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CreateNotificationRequest(BaseModel):
    user_id: int
    notif_type: str = "system"
    title: str
    body: str
    icon: str = "ph-bell"
    action: str = ""


# ── 路由 ──────────────────────────────────────────────────────────────────────

@router.post("/token")
def register_push_token(
    data: PushTokenRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """注册/更新设备推送 token"""
    existing = db.query(PushToken).filter(
        PushToken.user_id == current_user.id,
        PushToken.platform == data.platform
    ).first()
    if existing:
        existing.token = data.token
        existing.updated_at = datetime.utcnow()
    else:
        token = PushToken(
            user_id=current_user.id,
            platform=data.platform,
            token=data.token
        )
        db.add(token)
    db.commit()
    return {"success": True, "message": "Token 已注册"}


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的通知列表"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    notifs = query.order_by(Notification.created_at.desc()).limit(50).all()
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取未读通知数量"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return {"unread_count": count}


@router.put("/{notif_id}/read")
def mark_as_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记单条通知为已读"""
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="通知不存在")
    notif.is_read = True
    db.commit()
    return {"success": True}


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记所有通知为已读"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"success": True}


@router.delete("/{notif_id}")
def delete_notification(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除通知"""
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="通知不存在")
    db.delete(notif)
    db.commit()
    return {"success": True}


# ── 内部工具函数（供其他模块调用）────────────────────────────────────────────

def create_notification(
    db: Session,
    user_id: int,
    notif_type: str,
    title: str,
    body: str,
    icon: str = "ph-bell",
    action: str = ""
) -> Notification:
    """创建一条通知记录（内部调用）"""
    notif = Notification(
        user_id=user_id,
        notif_type=notif_type,
        title=title,
        body=body,
        icon=icon,
        action=action
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
