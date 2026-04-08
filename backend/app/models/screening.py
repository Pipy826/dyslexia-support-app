from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    game_type = Column(String(50), nullable=False)  # 'visual', 'spelling', 'comprehension'
    score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=True)  # 'low', 'medium', 'high'
    behavior_data = Column(Text, nullable=True)  # JSON string
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="screenings")
    dimension_scores = relationship("DimensionScore", back_populates="screening", cascade="all, delete-orphan")


class DimensionScore(Base):
    __tablename__ = "dimension_scores"

    id = Column(Integer, primary_key=True, index=True)
    screening_id = Column(Integer, ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False, index=True)
    dimension = Column(String(50), nullable=False)  # 'visual', 'spelling', 'reading', 'attention'
    score = Column(Integer, nullable=False)
    raw_data = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    screening = relationship("Screening", back_populates="dimension_scores")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    screening_id = Column(Integer, ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Integer, nullable=True)
    risk_level = Column(String(20), nullable=True)
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    dimensions = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="reports")
    screening = relationship("Screening")
