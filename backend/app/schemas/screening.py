from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class DimensionScoreCreate(BaseModel):
    dimension: str
    score: int
    raw_data: Optional[str] = None


class ScreeningStart(BaseModel):
    child_id: int
    game_type: str  # 'visual', 'spelling', 'comprehension'


class AnswerItem(BaseModel):
    question_id: str
    answer: Any
    time_spent: int  # seconds


class ScreeningSubmit(BaseModel):
    screening_id: int
    answers: List[AnswerItem]
    behavior_data: Optional[Dict[str, Any]] = None


class ScreeningResponse(BaseModel):
    id: int
    child_id: int
    game_type: str
    score: int
    risk_level: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionOption(BaseModel):
    id: str
    type: str
    title: str
    instruction: str
    options: List[str]
    correct_index: int
    audio_url: Optional[str] = None
    time_limit: int = 10


class GameQuestionsResponse(BaseModel):
    questions: List[QuestionOption]
    game_type: str
    difficulty: str = "L1"
