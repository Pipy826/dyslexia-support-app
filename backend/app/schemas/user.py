from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    username: Optional[str] = None
    password: str
    phone: Optional[str] = None
    code: Optional[str] = None
    invite_code: Optional[str] = None  # 邀请码（可选）

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 6:
            raise ValueError("密码不能为空且长度不能少于6位")
        if len(v) > 128:
            raise ValueError("密码不能超过128位")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("用户名不能少于2个字符")
        if len(v) > 50:
            raise ValueError("用户名不能超过50个字符")
        # 只允许字母、数字、中文、下划线、连字符
        if not re.match(r'^[\w\u4e00-\u9fa5\-]+$', v):
            raise ValueError("用户名只能包含字母、数字、中文、下划线或连字符")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("手机号格式不正确，请输入11位有效手机号")
        return v

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^\d{4,6}$', v):
            raise ValueError("验证码格式不正确")
        return v


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username_login(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("账号不能为空")
        if len(v) > 100:
            raise ValueError("账号格式不正确")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password_login(cls, v: str) -> str:
        if not v:
            raise ValueError("密码不能为空")
        if len(v) > 128:
            raise ValueError("密码格式不正确")
        return v


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
