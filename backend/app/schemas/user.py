from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: Optional[str] = None
    password: str
    phone: Optional[str] = None
    code: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 6:
            raise ValueError("密码不能为空且长度不能少于6位")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
