from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from pydantic import BaseModel
from typing import Optional
import random
import time
import threading
import logging

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..config import settings
from .deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])

# {phone: {"code": "1234", "expires_at": timestamp}}
# 使用线程锁保证并发安全
verification_codes: dict = {}
_codes_lock = threading.Lock()

CODE_EXPIRE_SECONDS = 300  # 5分钟过期


def _send_sms(phone: str, code: str) -> bool:
    """
    发送短信验证码。
    支持阿里云SMS和腾讯云SMS，通过环境变量 SMS_PROVIDER 切换。
    未配置时返回 False（DEBUG 模式下不影响功能）。

    环境变量配置示例（backend/.env）：
      # 阿里云
      SMS_PROVIDER=aliyun
      SMS_ACCESS_KEY=your_access_key_id
      SMS_SECRET_KEY=your_access_key_secret
      SMS_SIGN_NAME=悦读小灯塔
      SMS_TEMPLATE_CODE=SMS_xxxxxxxxx

      # 腾讯云
      SMS_PROVIDER=tencent
      SMS_ACCESS_KEY=your_secret_id
      SMS_SECRET_KEY=your_secret_key
      SMS_APP_ID=your_sms_app_id
      SMS_SIGN_NAME=悦读小灯塔
      SMS_TEMPLATE_CODE=your_template_id
    """
    provider = getattr(settings, 'SMS_PROVIDER', '') or ''
    access_key = getattr(settings, 'SMS_ACCESS_KEY', '') or ''
    secret_key = getattr(settings, 'SMS_SECRET_KEY', '') or ''
    sign_name = getattr(settings, 'SMS_SIGN_NAME', '悦读小灯塔') or '悦读小灯塔'
    template_code = getattr(settings, 'SMS_TEMPLATE_CODE', '') or ''

    if not provider or not access_key or not secret_key:
        logger.debug(f"SMS not configured, skipping send to {phone}")
        return False

    try:
        if provider.lower() == 'aliyun':
            return _send_aliyun_sms(phone, code, access_key, secret_key, sign_name, template_code)
        elif provider.lower() == 'tencent':
            app_id = getattr(settings, 'SMS_APP_ID', '') or ''
            return _send_tencent_sms(phone, code, access_key, secret_key, app_id, sign_name, template_code)
        else:
            logger.warning(f"Unknown SMS provider: {provider}")
            return False
    except Exception as e:
        logger.error(f"SMS send failed: {e}")
        return False


def _send_aliyun_sms(phone, code, access_key, secret_key, sign_name, template_code) -> bool:
    """阿里云短信发送（需安装 alibabacloud-dysmsapi20170525）"""
    try:
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_dysmsapi20170525 import models as dysms_models
        import json

        config = open_api_models.Config(
            access_key_id=access_key,
            access_key_secret=secret_key,
            endpoint='dysmsapi.aliyuncs.com'
        )
        client = Client(config)
        request = dysms_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=sign_name,
            template_code=template_code,
            template_param=json.dumps({"code": code})
        )
        response = client.send_sms(request)
        if response.body.code == 'OK':
            logger.info(f"Aliyun SMS sent to {phone}")
            return True
        else:
            logger.error(f"Aliyun SMS failed: {response.body.message}")
            return False
    except ImportError:
        logger.warning("alibabacloud-dysmsapi20170525 not installed. Run: pip install alibabacloud-dysmsapi20170525")
        return False


def _send_tencent_sms(phone, code, secret_id, secret_key, app_id, sign_name, template_id) -> bool:
    """腾讯云短信发送（需安装 tencentcloud-sdk-python-sms）"""
    try:
        from tencentcloud.common import credential
        from tencentcloud.sms.v20210111 import sms_client, models as sms_models

        cred = credential.Credential(secret_id, secret_key)
        client = sms_client.SmsClient(cred, "ap-guangzhou")
        req = sms_models.SendSmsRequest()
        req.SmsSdkAppId = app_id
        req.SignName = sign_name
        req.TemplateId = template_id
        req.TemplateParamSet = [code]
        req.PhoneNumberSet = [f"+86{phone}"]
        resp = client.SendSms(req)
        if resp.SendStatusSet and resp.SendStatusSet[0].Code == 'Ok':
            logger.info(f"Tencent SMS sent to {phone}")
            return True
        else:
            code_resp = resp.SendStatusSet[0].Code if resp.SendStatusSet else 'unknown'
            logger.error(f"Tencent SMS failed: {code_resp}")
            return False
    except ImportError:
        logger.warning("tencentcloud-sdk-python-sms not installed. Run: pip install tencentcloud-sdk-python-sms")
        return False


def _get_code(phone: str):
    """线程安全地获取验证码条目"""
    with _codes_lock:
        return verification_codes.get(phone)


def _set_code(phone: str, code: str):
    """线程安全地设置验证码"""
    with _codes_lock:
        verification_codes[phone] = {
            "code": code,
            "expires_at": time.time() + CODE_EXPIRE_SECONDS
        }


def _delete_code(phone: str):
    """线程安全地删除验证码"""
    with _codes_lock:
        verification_codes.pop(phone, None)


def _validate_code(phone: str, code: str) -> tuple[bool, str]:
    """
    验证验证码，返回 (is_valid, error_message)。
    验证成功后自动删除验证码（消耗型）。
    """
    with _codes_lock:
        entry = verification_codes.get(phone)
        if not entry:
            return False, "验证码不存在或已过期"
        if time.time() > entry["expires_at"]:
            verification_codes.pop(phone, None)
            return False, "验证码已过期，请重新获取"
        if entry["code"] != code:
            return False, "验证码错误"
        # 验证成功，消耗验证码
        verification_codes.pop(phone, None)
        return True, ""


class PhoneRequest(BaseModel):
    phone: str


class LoginByCodeRequest(BaseModel):
    phone: str
    code: str


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new parent user"""
    # 手机号注册时必须验证验证码；纯用户名注册（无手机号）则跳过
    if user_data.phone:
        if not user_data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号注册必须提供验证码"
            )
        valid, err = _validate_code(user_data.phone, user_data.code)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    
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
def login_by_code(data: LoginByCodeRequest, db: Session = Depends(get_db)):
    """Login with phone + verification code (auto-register if not exists)"""
    valid, err = _validate_code(data.phone, data.code)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    # 查找或自动注册
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        import secrets
        user = User(
            username=data.phone,
            password_hash=get_password_hash(secrets.token_hex(16)),
            phone=data.phone
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
    entry = _get_code(phone)
    if entry and time.time() < entry["expires_at"] - CODE_EXPIRE_SECONDS + 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送太频繁，请60秒后再试"
        )

    code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    _set_code(phone, code)

    # 尝试发送真实短信（需配置 SMS_PROVIDER / SMS_ACCESS_KEY / SMS_SECRET_KEY）
    sms_sent = _send_sms(phone, code)

    # DEBUG 模式下始终打印到日志（方便开发调试）
    if settings.DEBUG:
        print(f"[DEV] 验证码 {phone}: {code}（{CODE_EXPIRE_SECONDS}秒内有效）")
    elif not sms_sent:
        # 生产环境且短信发送失败时，返回错误
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="短信发送失败，请稍后重试"
        )

    return {"message": "验证码已发送", "expires_in": CODE_EXPIRE_SECONDS}


@router.get("/verify-code")
def verify_code_check(phone: str, code: str):
    """Verify phone code (不消耗验证码，仅校验)"""
    with _codes_lock:
        entry = verification_codes.get(phone)
        if not entry:
            return {"valid": False, "reason": "验证码不存在"}
        if time.time() > entry["expires_at"]:
            verification_codes.pop(phone, None)
            return {"valid": False, "reason": "验证码已过期"}
        return {"valid": entry["code"] == code}


# ── 账号信息编辑 ──────────────────────────────────────────────────────────────

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    phone_code: Optional[str] = None  # 修改手机号时需要验证码


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改用户名或手机号"""
    if data.username and data.username != current_user.username:
        existing = db.query(User).filter(
            User.username == data.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已被占用")
        current_user.username = data.username

    if data.phone and data.phone != current_user.phone:
        # 修改手机号需要验证码
        if not data.phone_code:
            raise HTTPException(status_code=400, detail="修改手机号需要提供验证码")
        valid, err = _validate_code(data.phone, data.phone_code)
        if not valid:
            raise HTTPException(status_code=400, detail=err)
        existing = db.query(User).filter(
            User.phone == data.phone,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="该手机号已被其他账号绑定")
        current_user.phone = data.phone

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改密码"""
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于6位")
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


# ── 微信小程序登录 ────────────────────────────────────────────────────────────

class WxLoginRequest(BaseModel):
    code: str  # wx.login() 返回的 code


@router.post("/wx-login", response_model=Token)
async def wx_login(data: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录。
    1. 用 code 换取 openid（调用微信 jscode2session 接口）
    2. 用 openid 查找或创建用户
    3. 返回 JWT token
    """
    import httpx

    wx_appid = getattr(settings, "WX_APPID", "")
    wx_secret = getattr(settings, "WX_SECRET", "")

    if not wx_appid or not wx_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="微信登录未配置，请在 .env 中设置 WX_APPID 和 WX_SECRET"
        )

    # 调用微信 jscode2session
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={
                    "appid": wx_appid,
                    "secret": wx_secret,
                    "js_code": data.code,
                    "grant_type": "authorization_code",
                },
            )
            wx_data = resp.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"微信服务请求失败: {str(e)}"
        )

    if "errcode" in wx_data and wx_data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {wx_data.get('errmsg', '未知错误')}"
        )

    openid = wx_data.get("openid")
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法获取微信 openid"
        )

    # 查找或创建用户（以 openid 为唯一标识）
    # 使用完整 openid 作为用户名，避免截断导致的冲突
    wx_username = f"wx_{openid}"
    user = db.query(User).filter(User.username == wx_username).first()

    if not user:
        # 首次微信登录，自动注册
        user = User(
            username=wx_username,
            password_hash=get_password_hash(openid),  # 用 openid 作为密码（不可逆）
            phone=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 生成 JWT
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7)
    )

    is_new_user = user.created_at.date() == datetime.utcnow().date()
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    ).model_dump() | {"is_new_user": is_new_user}
