from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


# 徽章定义常量
BADGE_DEFINITIONS = {
    "first_game": {
        "name": "初次探险",
        "icon": "🚀",
        "desc": "完成第一次能力探索",
    },
    "week_streak": {
        "name": "坚持一周",
        "icon": "🔥",
        "desc": "连续7天完成挑战",
    },
    "month_streak": {
        "name": "月度冠军",
        "icon": "🏆",
        "desc": "连续30天完成挑战",
    },
    "all_games": {
        "name": "全能探险家",
        "icon": "🌟",
        "desc": "完成全部6种游戏",
    },
    "perfect_score": {
        "name": "完美表现",
        "icon": "💎",
        "desc": "单次游戏正确率100%",
    },
    "speed_demon": {
        "name": "闪电侠",
        "icon": "⚡",
        "desc": "平均反应时间低于2秒",
    },
}

# 全部6种游戏类型
ALL_GAME_TYPES = {"visual", "spelling", "comprehension", "working_memory", "rapid_naming", "motor_coordination"}


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    reward_type = Column(String(50), nullable=True)  # 'star', 'badge', 'achievement'
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    earned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="rewards")
