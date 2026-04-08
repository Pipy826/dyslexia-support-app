from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class TrainingTaskCreate(BaseModel):
    child_id: int
    task_type: str
    task_name: Optional[str] = None
    scheduled_date: Optional[date] = None


class TrainingTaskUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None


class TrainingTaskResponse(BaseModel):
    id: int
    child_id: int
    task_type: str
    task_name: Optional[str] = None
    status: str
    progress: int
    scheduled_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GrowthRecordCreate(BaseModel):
    child_id: int
    record_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[str] = None


class GrowthRecordResponse(BaseModel):
    id: int
    child_id: int
    record_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[str] = Field(default=None, alias="meta_data")
    created_at: datetime

    class Config:
        from_attributes = True
