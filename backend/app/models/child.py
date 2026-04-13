from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=True)
    birth_date = Column(Date, nullable=False)
    grade = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    has_difficulty = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("User", back_populates="children")
    screenings = relationship("Screening", back_populates="child", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="child", cascade="all, delete-orphan")
    training_tasks = relationship("TrainingTask", back_populates="child", cascade="all, delete-orphan")
    growth_records = relationship("GrowthRecord", back_populates="child", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="child", cascade="all, delete-orphan")
