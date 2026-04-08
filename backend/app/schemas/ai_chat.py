from pydantic import BaseModel
from typing import Optional


class AIChatRequest(BaseModel):
    child_id: Optional[int] = None
    message: str


class AIChatResponse(BaseModel):
    reply: str
    conversation_id: Optional[int] = None
