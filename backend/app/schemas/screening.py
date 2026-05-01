from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class GameTypeEnum(str, Enum):
    """合法的游戏类型白名单，防止注入任意值"""
    visual = "visual"
    spelling = "spelling"
    comprehension = "comprehension"
    sort_order = "sort_order"
    working_memory = "working_memory"
    rapid_naming = "rapid_naming"
    motor_coordination = "motor_coordination"


class DimensionScoreCreate(BaseModel):
    dimension: str
    score: int
    raw_data: Optional[str] = None


class ScreeningStart(BaseModel):
    child_id: int
    game_type: GameTypeEnum  # 强制枚举，防止注入任意值


class AnswerItem(BaseModel):
    question_id: str
    answer: Any
    time_spent: int  # seconds
    reaction_time: Optional[int] = None   # 首次点击反应时间（毫秒）
    change_count: Optional[int] = None    # 修改次数
    is_timeout: Optional[bool] = None     # 是否超时

    @field_validator("question_id")
    @classmethod
    def validate_question_id(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("question_id 过长")
        return v

    @field_validator("time_spent")
    @classmethod
    def validate_time_spent(cls, v: int) -> int:
        if v < 0 or v > 3600:
            raise ValueError("time_spent 超出合理范围（0-3600秒）")
        return v


# behavior_data 允许的顶层键白名单，防止注入任意大字段
_ALLOWED_BEHAVIOR_KEYS = {"device_info", "environment", "session_id"}


class ScreeningSubmit(BaseModel):
    screening_id: int
    answers: List[AnswerItem]
    behavior_data: Optional[Dict[str, Any]] = None

    @field_validator("answers")
    @classmethod
    def validate_answers_count(cls, v: List[AnswerItem]) -> List[AnswerItem]:
        if len(v) > 100:
            raise ValueError("答题数量超出限制（最多100题）")
        return v

    @field_validator("behavior_data")
    @classmethod
    def sanitize_behavior_data(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """只保留白名单内的顶层键，防止注入任意大字段"""
        if v is None:
            return v
        return {k: val for k, val in v.items() if k in _ALLOWED_BEHAVIOR_KEYS}


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
