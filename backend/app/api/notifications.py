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
    """获取未读通知数量（包含系统通知和 AI 推送通知）"""
    from ..models.notification import AINotification

    # 系统通知未读数
    system_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    # AI 推送通知未读数
    ai_count = db.query(AINotification).filter(
        AINotification.parent_id == current_user.id,
        AINotification.is_read == False,
    ).count()

    return {"unread_count": system_count + ai_count, "count": system_count + ai_count}


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


# ── AI 个性化推送通知（基于游戏行为数据）────────────────────────────────────

# 游戏类型名称映射
GAME_NAME_MAP = {
    "visual": "找不同游戏",
    "spelling": "认字游戏",
    "comprehension": "阅读理解游戏",
    "working_memory": "记忆力游戏",
    "rapid_naming": "快速命名游戏",
    "motor_coordination": "精细动作游戏",
}

# 能力标签映射（简化版，用于推送文本）
ABILITY_LABEL_MAP = {
    "visual": "视觉辨别能力",
    "spelling": "文字识别能力",
    "comprehension": "阅读理解能力",
    "working_memory": "工作记忆能力",
    "rapid_naming": "快速命名能力",
    "motor_coordination": "精细动作能力",
}


class AINotificationResponse(BaseModel):
    id: int
    content: str
    game_type: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarkReadRequest(BaseModel):
    notification_ids: List[int]


@router.get("/list", response_model=dict)
def get_ai_notifications(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取最近7天的 AI 个性化推送通知列表（分页）"""
    from datetime import timedelta
    from ..models.notification import AINotification

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    query = db.query(AINotification).filter(
        AINotification.parent_id == current_user.id,
        AINotification.created_at >= seven_days_ago,
    ).order_by(AINotification.created_at.desc())

    total = query.count()
    unread_count = db.query(AINotification).filter(
        AINotification.parent_id == current_user.id,
        AINotification.is_read == False,
    ).count()

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return {
        "notifications": [
            {
                "id": n.id,
                "content": n.content,
                "game_type": n.game_type,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in items
        ],
        "total": total,
        "unread_count": unread_count,
    }


@router.post("/mark-read")
def mark_ai_notifications_read(
    data: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量标记 AI 推送通知为已读"""
    from ..models.notification import AINotification

    if data.notification_ids:
        db.query(AINotification).filter(
            AINotification.id.in_(data.notification_ids),
            AINotification.parent_id == current_user.id,
        ).update({"is_read": True}, synchronize_session=False)
    else:
        # 空列表时标记全部已读
        db.query(AINotification).filter(
            AINotification.parent_id == current_user.id,
            AINotification.is_read == False,
        ).update({"is_read": True}, synchronize_session=False)

    db.commit()
    return {"success": True}


def generate_and_push_notification(
    child_id: int,
    game_type: str,
    score: int,
    behavior_data: dict,
    db_session_factory,
) -> None:
    """
    游戏提交后由 BackgroundTasks 调用，根据孩子游戏行为生成 AI 个性化推送通知并写入数据库。
    使用独立的数据库会话，避免与主请求的 session 冲突。

    推送逻辑：
    - 犹豫次数 >= 3：提示家长关注该能力
    - 分数 >= 75：正向鼓励
    - 其他：普通完成提示
    """
    import logging
    from ..models.notification import AINotification
    from ..models.child import Child

    logger = logging.getLogger(__name__)

    try:
        db = db_session_factory()
        try:
            child = db.query(Child).filter(Child.id == child_id).first()
            if not child or not child.parent_id:
                return

            parent_id = child.parent_id
            game_name = GAME_NAME_MAP.get(game_type, "文字游戏")
            ability_label = ABILITY_LABEL_MAP.get(game_type, "读写能力")

            # 分析行为数据
            hesitation_count = 0
            if behavior_data:
                answers = behavior_data.get("answers_detail", [])
                hesitation_count = sum(
                    1 for ans in answers
                    if ans.get("change_count", 0) >= 2
                )

            # 生成推送文本
            if hesitation_count >= 3:
                content = (
                    f"{child.name}今天在{game_name}里卡住了{hesitation_count}次，"
                    f"建议多关注{ability_label}的练习～"
                )
            elif score >= 75:
                content = (
                    f"{child.name}在{game_name}中表现很棒，获得了高分！"
                    f"快来看看今天的能力地图～"
                )
            else:
                content = (
                    f"{child.name}今天完成了{game_name}挑战，"
                    f"{ability_label}继续加油！"
                )

            notification = AINotification(
                parent_id=parent_id,
                child_id=child_id,
                content=content,
                game_type=game_type,
                is_read=False,
            )
            db.add(notification)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"generate_and_push_notification failed for child {child_id}: {e}")
