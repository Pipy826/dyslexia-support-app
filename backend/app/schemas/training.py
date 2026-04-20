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
    # 训练结果字段（完成后填充）
    correct_count: Optional[int] = None
    total_count: Optional[int] = None
    accuracy: Optional[int] = None

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

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "serialize_by_alias": False,  # 序列化时使用字段名 metadata，而非别名 meta_data
    }
