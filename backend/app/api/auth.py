from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from pydantic import BaseModel
import random
import time

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..config import settings
from .deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

# {phone: {"code": "1234", "expires_at": timestamp}}
verification_codes: dict = {}

CODE_EXPIRE_SECONDS = 300  # 5分钟过期


class PhoneRequest(BaseModel):
    phone: str


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new parent user"""
    if user_data.phone and user_data.code:
        entry = verification_codes.get(user_data.phone)
        if not entry:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码不存在或已过期")
        if time.time() > entry["expires_at"]:
            del verification_codes[user_data.phone]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码已过期，请重新获取")
        if entry["code"] != user_data.code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误")
        del verification_codes[user_data.phone]
    
    if user_data.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被注册"
            )

    # 手机号唯一性检查
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已注册"
            )

    final_username = user_data.username or user_data.phone
    if not final_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请提供用户名或手机号")

    user = User(
        username=final_username,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with username/phone and password"""
    # 支持用户名或手机号登录
    user = db.query(User).filter(
        (User.username == user_data.username) | (User.phone == user_data.username)
    ).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login-by-code", response_model=Token)
def login_by_code(phone: str, code: str, db: Session = Depends(get_db)):
    """Login with phone + verification code (auto-register if not exists)"""
    entry = verification_codes.get(phone)
    if not entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码不存在或已过期")
    if time.time() > entry["expires_at"]:
        del verification_codes[phone]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码已过期，请重新获取")
    if entry["code"] != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误")
    del verification_codes[phone]

    # 查找或自动注册
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        import secrets
        user = User(
            username=phone,
            password_hash=get_password_hash(secrets.token_hex(16)),
            phone=phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return UserResponse.model_validate(current_user)


@router.post("/send-code")
def send_verification_code(request: PhoneRequest):
    """Send verification code to phone"""
    phone = request.phone
    if len(phone) != 11 or not phone.startswith('1'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )

    # 防刷：60秒内不能重复发送
    entry = verification_codes.get(phone)
    if entry and time.time() < entry["expires_at"] - CODE_EXPIRE_SECONDS + 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送太频繁，请60秒后再试"
        )

    code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    verification_codes[phone] = {
        "code": code,
        "expires_at": time.time() + CODE_EXPIRE_SECONDS
    }

    # TODO: 生产环境接入真实短信服务（如阿里云SMS、腾讯云SMS）
    # 开发模式下将验证码打印到日志
    print(f"[DEV] 验证码 {phone}: {code}（{CODE_EXPIRE_SECONDS}秒内有效）")

    return {"message": "验证码已发送", "expires_in": CODE_EXPIRE_SECONDS}


@router.post("/verify-code")
def verify_code(request: PhoneRequest, code: str):
    """Verify phone code (不消耗验证码，仅校验)"""
    phone = request.phone
    entry = verification_codes.get(phone)
    if not entry:
        return {"valid": False, "reason": "验证码不存在"}
    if time.time() > entry["expires_at"]:
        del verification_codes[phone]
        return {"valid": False, "reason": "验证码已过期"}
    return {"valid": entry["code"] == code}
