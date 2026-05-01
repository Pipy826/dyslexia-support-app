from pydantic import BaseModel
from typing import Optional


class AIChatRequest(BaseModel):
    child_id: Optional[int] = None
    message: str


class AIChatResponse(BaseModel):
    reply: str
    conversation_id: Optional[int] = None
    need_professional: bool = False  # True 时前端显示"联系专业导师"按钮
