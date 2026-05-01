from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class TrainingTask(Base):
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)
    task_name = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    scheduled_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    # 训练结果
    correct_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="training_tasks")


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    record_type = Column(String(50), nullable=True)  # 'screening', 'training', 'milestone'
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    meta_data = Column("metadata", Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="growth_records")


class CheckInRecord(Base):
    __tablename__ = "check_in_records"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    check_in_date = Column(Date, nullable=False)
    streak_count = Column(Integer, default=1)  # 连续天数
    reward_granted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="check_in_records")
