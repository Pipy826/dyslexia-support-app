"""
AI 站内推送通知数据模型
用于存储基于孩子游戏行为生成的个性化推送通知
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class AINotification(Base):
    """AI 个性化推送通知表（基于游戏行为数据生成）"""
    __tablename__ = "ai_notifications"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)          # AI 生成的推送文本
    game_type = Column(String(50), nullable=True)   # 触发推送的游戏类型
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    parent = relationship("User", foreign_keys=[parent_id])
    child = relationship("Child", foreign_keys=[child_id])
