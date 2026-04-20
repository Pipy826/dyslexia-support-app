from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ChildCreate(BaseModel):
    name: str
    gender: Optional[str] = None
    birth_date: date
    grade: Optional[str] = None
    avatar_url: Optional[str] = None
    has_difficulty: Optional[bool] = None
    has_professional_eval: Optional[bool] = None


class ChildUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    grade: Optional[str] = None
    avatar_url: Optional[str] = None
    has_difficulty: Optional[bool] = None
    has_professional_eval: Optional[bool] = None


class ChildResponse(BaseModel):
    id: int
    parent_id: int
    name: str
    gender: Optional[str] = None
    birth_date: date
    grade: Optional[str] = None
    avatar_url: Optional[str] = None
    has_difficulty: Optional[bool] = None
    has_professional_eval: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True
