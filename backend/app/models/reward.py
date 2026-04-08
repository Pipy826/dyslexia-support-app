from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


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
