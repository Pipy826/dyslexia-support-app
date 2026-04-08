from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
import random

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..config import settings
from .deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

verification_codes = {}


class PhoneRequest(BaseModel):
    phone: str


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new parent user"""
    if user_data.phone and user_data.code:
        if verification_codes.get(user_data.phone) != user_data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        del verification_codes[user_data.phone]
    
    if user_data.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

    user = User(
        username=user_data.username or user_data.phone,
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
    """Login with username and password"""
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


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
            detail="Invalid phone number"
        )
    
    code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    verification_codes[phone] = code
    
    return {"message": "Code sent successfully", "code": code}


@router.post("/verify-code")
def verify_code(request: PhoneRequest, code: str):
    """Verify phone code"""
    phone = request.phone
    if verification_codes.get(phone) == code:
        del verification_codes[phone]
        return {"valid": True}
    return {"valid": False}
