from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from pydantic import BaseModel
from typing import Optional
import random
import time
import threading
import logging
import re

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..config import settings
from .deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])

# ── 验证码存储（内存，线程安全） ──────────────────────────────────────────────
# {phone: {"code": "1234", "expires_at": timestamp, "attempts": int}}
verification_codes: dict = {}
_codes_lock = threading.Lock()

CODE_EXPIRE_SECONDS = 300       # 5分钟过期
MAX_CODE_ATTEMPTS = 5           # 验证码最多尝试次数

# ── 速率限制（内存实现，无需额外依赖） ──────────────────────────────────────
# {key: [timestamp, ...]}  key = "login:{ip}" 或 "code:{phone}"
_rate_limit_store: dict = {}
_rate_limit_lock = threading.Lock()


def _check_rate_limit(key: str, max_calls: int, window_seconds: int) -> bool:
    """
    检查速率限制。
    返回 True 表示允许，False 表示超限。
    自动清理过期记录。
    """
    now = time.time()
    with _rate_limit_lock:
        timestamps = _rate_limit_store.get(key, [])
        # 清理窗口外的旧记录
        timestamps = [t for t in timestamps if now - t < window_seconds]
        if len(timestamps) >= max_calls:
            _rate_limit_store[key] = timestamps
            return False
        timestamps.append(now)
        _rate_limit_store[key] = timestamps
        return True


def _get_client_ip(request: Request) -> str:
    """获取客户端真实 IP（兼容反向代理）"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


# ── 短信发送 ──────────────────────────────────────────────────────────────────

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
        logger.debug("SMS not configured, skipping send to [PHONE_REDACTED]")
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
        # 不在日志中打印完整异常，避免泄露 key
        logger.error(f"SMS send failed: {type(e).__name__}")
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
            logger.info("Aliyun SMS sent successfully")
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
            logger.info("Tencent SMS sent successfully")
            return True
        else:
            code_resp = resp.SendStatusSet[0].Code if resp.SendStatusSet else 'unknown'
            logger.error(f"Tencent SMS failed: {code_resp}")
            return False
    except ImportError:
        logger.warning("tencentcloud-sdk-python-sms not installed. Run: pip install tencentcloud-sdk-python-sms")
        return False


# ── 验证码操作（线程安全） ────────────────────────────────────────────────────

def _get_code(phone: str):
    """线程安全地获取验证码条目"""
    with _codes_lock:
        return verification_codes.get(phone)


def _set_code(phone: str, code: str):
    """线程安全地设置验证码"""
    with _codes_lock:
        verification_codes[phone] = {
            "code": code,
            "expires_at": time.time() + CODE_EXPIRE_SECONDS,
            "attempts": 0,
        }


def _delete_code(phone: str):
    """线程安全地删除验证码"""
    with _codes_lock:
        verification_codes.pop(phone, None)


def _validate_code(phone: str, code: str) -> tuple[bool, str]:
    """
    验证验证码，返回 (is_valid, error_message)。
    验证成功后自动删除验证码（消耗型）。
    超过最大尝试次数后自动作废。
    """
    with _codes_lock:
        entry = verification_codes.get(phone)
        if not entry:
            return False, "验证码不存在或已过期"
        if time.time() > entry["expires_at"]:
            verification_codes.pop(phone, None)
            return False, "验证码已过期，请重新获取"
        # 尝试次数限制
        if entry.get("attempts", 0) >= MAX_CODE_ATTEMPTS:
            verification_codes.pop(phone, None)
            return False, "验证码已失效，请重新获取"
        if entry["code"] != code:
            entry["attempts"] = entry.get("attempts", 0) + 1
            return False, "验证码错误"
        # 验证成功，消耗验证码
        verification_codes.pop(phone, None)
        return True, ""


# ── 请求体模型 ────────────────────────────────────────────────────────────────

class PhoneRequest(BaseModel):
    phone: str


class LoginByCodeRequest(BaseModel):
    phone: str
    code: str


# ── 注册 ──────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=Token)
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new parent user"""
    # IP 级别速率限制：每个 IP 每小时最多注册 10 次
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"register:{ip}", max_calls=10, window_seconds=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="注册请求过于频繁，请稍后再试"
        )

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

    # 处理邀请码（可选，失败不影响注册）
    invite_code = getattr(user_data, 'invite_code', None)
    if invite_code:
        try:
            from ..models.invite import InviteRecord
            invite_record = db.query(InviteRecord).filter(
                InviteRecord.invite_code == invite_code,
                InviteRecord.invitee_id == None,  # noqa: E711
            ).first()
            if invite_record:
                invite_record.invitee_id = user.id
                invite_record.used_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.warning(f"处理邀请码失败（不影响注册）: {e}")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# ── 密码登录 ──────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with username/phone and password"""
    # IP 级别速率限制：每个 IP 每分钟最多 10 次，每小时最多 30 次
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"login_min:{ip}", max_calls=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="登录尝试过于频繁，请1分钟后再试"
        )
    if not _check_rate_limit(f"login_hr:{ip}", max_calls=30, window_seconds=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="登录尝试过于频繁，请1小时后再试"
        )

    # 支持用户名或手机号登录
    user = db.query(User).filter(
        (User.username == user_data.username) | (User.phone == user_data.username)
    ).first()

    # 统一错误信息，防止用户枚举
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


# ── 验证码登录 ────────────────────────────────────────────────────────────────

@router.post("/login-by-code", response_model=Token)
def login_by_code(request: Request, data: LoginByCodeRequest, db: Session = Depends(get_db)):
    """Login with phone + verification code (auto-register if not exists)"""
    # IP 级别速率限制
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"login_code:{ip}", max_calls=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试"
        )

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


# ── 当前用户信息 ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return UserResponse.model_validate(current_user)


# ── 发送验证码 ────────────────────────────────────────────────────────────────

@router.post("/send-code")
def send_verification_code(request: Request, req_body: PhoneRequest):
    """Send verification code to phone"""
    phone = req_body.phone

    # 手机号格式校验（更严格的正则）
    if not re.match(r'^1[3-9]\d{9}$', phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )

    # IP 级别速率限制：每个 IP 每分钟最多 5 次
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"send_code_ip:{ip}", max_calls=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试"
        )

    # 手机号级别：60秒内不能重复发送
    entry = _get_code(phone)
    if entry and time.time() < entry["expires_at"] - CODE_EXPIRE_SECONDS + 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送太频繁，请60秒后再试"
        )

    # 使用 secrets 模块生成密码学安全的随机验证码
    import secrets as _secrets
    code = ''.join([str(_secrets.randbelow(10)) for _ in range(4)])
    _set_code(phone, code)

    # 尝试发送真实短信（需配置 SMS_PROVIDER / SMS_ACCESS_KEY / SMS_SECRET_KEY）
    sms_sent = _send_sms(phone, code)

    # DEBUG 模式下始终打印到日志（方便开发调试）
    if settings.DEBUG:
        logger.debug(f"[DEV] 验证码已生成，手机号末4位: ...{phone[-4:]}，验证码: {code}（{CODE_EXPIRE_SECONDS}秒内有效）")
    elif not sms_sent:
        # 生产环境且短信发送失败时，返回错误
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="短信发送失败，请稍后重试"
        )

    return {"message": "验证码已发送", "expires_in": CODE_EXPIRE_SECONDS}


# ── 验证码校验（不消耗） ──────────────────────────────────────────────────────

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
        # 用户名长度限制
        if len(data.username) > 50:
            raise HTTPException(status_code=400, detail="用户名不能超过50个字符")
        existing = db.query(User).filter(
            User.username == data.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已被占用")
        current_user.username = data.username

    if data.phone and data.phone != current_user.phone:
        # 手机号格式校验
        if not re.match(r'^1[3-9]\d{9}$', data.phone):
            raise HTTPException(status_code=400, detail="手机号格式不正确")
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
    if len(data.new_password) > 128:
        raise HTTPException(status_code=400, detail="新密码不能超过128位")
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


# ── 儿童模式退出密码验证 ──────────────────────────────────────────────────────

class VerifyPasswordRequest(BaseModel):
    password: str


@router.post("/verify-password")
def verify_password_for_exit(
    request: Request,
    data: VerifyPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    验证当前登录用户的密码（用于儿童模式退出验证）。
    不颁发新 token，仅返回验证结果。
    与 /login 不同，此接口需要携带有效 JWT，不会触发全局登出拦截器。
    """
    # IP 级别速率限制：每分钟最多 10 次，防止暴力破解
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"verify_pwd:{ip}", max_calls=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="验证过于频繁，请稍后再试"
        )

    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )

    return {"valid": True}


# ── 微信小程序登录 ────────────────────────────────────────────────────────────

class WxLoginRequest(BaseModel):
    code: str  # wx.login() 返回的 code
    guest_id: Optional[str] = None  # 游客 ID，用于数据迁移


def migrate_guest_data(guest_id: str, user_id: int, db: Session) -> int:
    """
    将游客筛查记录迁移到已登录用户。
    查找 guest_id 匹配的 Screening 记录，将其 guest_id 清空（标记为已迁移）。
    返回迁移的记录数量。
    """
    from ..models.screening import Screening

    screenings = db.query(Screening).filter(
        Screening.guest_id == guest_id
    ).all()

    count = len(screenings)
    for screening in screenings:
        screening.guest_id = None  # 清空 guest_id，标记为已迁移

    if count > 0:
        db.commit()

    return count


@router.post("/wx-login", response_model=Token)
async def wx_login(request: Request, data: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录。
    1. 用 code 换取 openid（调用微信 jscode2session 接口）
    2. 用 wechat_openid 字段查找或创建用户
    3. 若传入 guest_id，迁移游客数据
    4. 返回 JWT token 及迁移数量
    """
    import httpx

    # IP 速率限制
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"wx_login:{ip}", max_calls=20, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试"
        )

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
            detail="微信服务请求失败，请稍后重试"
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

    # 用 wechat_openid 字段查找用户（兼容旧的 username=wx_{openid} 方式）
    user = db.query(User).filter(User.wechat_openid == openid).first()

    # 兼容旧数据：尝试通过旧 username 格式查找并升级
    if not user:
        old_username = f"wx_{openid}"
        user = db.query(User).filter(User.username == old_username).first()
        if user:
            # 升级旧用户：写入 wechat_openid 字段
            user.wechat_openid = openid
            db.commit()
            db.refresh(user)

    if not user:
        import secrets as _secrets
        user = User(
            username=f"wx_{openid[:8]}",
            password_hash=get_password_hash(_secrets.token_hex(32)),
            phone=None,
            wechat_openid=openid,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 游客数据迁移
    migrated_count = 0
    if data.guest_id:
        migrated_count = migrate_guest_data(data.guest_id, user.id, db)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7)
    )

    is_new_user = user.created_at.date() == datetime.utcnow().date()
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    ).model_dump() | {"is_new_user": is_new_user, "migrated_count": migrated_count}


# ── 邀请码系统 ────────────────────────────────────────────────────────────────

@router.get("/invite-code")
def get_invite_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的邀请码（不存在则生成）"""
    import random
    import string
    from ..models.invite import InviteRecord

    # 查找已有邀请码
    existing = db.query(InviteRecord).filter(
        InviteRecord.inviter_id == current_user.id,
        InviteRecord.invitee_id == None,  # noqa: E711
    ).first()

    if existing:
        return {"invite_code": existing.invite_code}

    # 生成新邀请码（8位字母数字）
    for _ in range(10):  # 最多重试10次避免碰撞
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not db.query(InviteRecord).filter(InviteRecord.invite_code == code).first():
            record = InviteRecord(
                inviter_id=current_user.id,
                invite_code=code,
            )
            db.add(record)
            db.commit()
            return {"invite_code": code}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="生成邀请码失败，请重试"
    )
