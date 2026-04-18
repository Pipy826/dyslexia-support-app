from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ReportResponse(BaseModel):
    id: int
    child_id: int
    screening_id: int
    overall_score: Optional[int] = None
    risk_level: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    dimensions: Optional[str] = None  # JSON string
    game_type: Optional[str] = None   # 来自关联的 Screening，方便前端展示
    created_at: datetime

    class Config:
        from_attributes = True


class ReportDetailResponse(ReportResponse):
    child_name: str
    child_age: int
