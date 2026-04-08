from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class TrainingTask(Base):
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)  # 'visual', 'spelling', 'reading'
    task_name = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")  # 'pending', 'in_progress', 'completed'
    progress = Column(Integer, default=0)  # 0-100
    scheduled_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
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
