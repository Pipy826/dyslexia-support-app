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

router = APIRouter(prefix="/api/auth", tags=["璁よ瘉"])

# 鈹€鈹€ 楠岃瘉鐮佸瓨鍌紙鍐呭瓨锛岀嚎绋嬪畨鍏級 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# {phone: {"code": "1234", "expires_at": timestamp, "attempts": int}}
verification_codes: dict = {}
_codes_lock = threading.Lock()

CODE_EXPIRE_SECONDS = 300       # 5鍒嗛挓杩囨湡
MAX_CODE_ATTEMPTS = 5           # 楠岃瘉鐮佹渶澶氬皾璇曟鏁?
# 鈹€鈹€ 閫熺巼闄愬埗锛堝唴瀛樺疄鐜帮紝鏃犻渶棰濆渚濊禆锛?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# {key: [timestamp, ...]}  key = "login:{ip}" 鎴?"code:{phone}"
_rate_limit_store: dict = {}
_rate_limit_lock = threading.Lock()


def _check_rate_limit(key: str, max_calls: int, window_seconds: int) -> bool:
    """
    妫€鏌ラ€熺巼闄愬埗銆?    杩斿洖 True 琛ㄧず鍏佽锛孎alse 琛ㄧず瓒呴檺銆?    鑷姩娓呯悊杩囨湡璁板綍銆?    """
    now = time.time()
    with _rate_limit_lock:
        timestamps = _rate_limit_store.get(key, [])
        # 娓呯悊绐楀彛澶栫殑鏃ц褰?        timestamps = [t for t in timestamps if now - t < window_seconds]
        if len(timestamps) >= max_calls:
            _rate_limit_store[key] = timestamps
            return False
        timestamps.append(now)
        _rate_limit_store[key] = timestamps
        return True


def _get_client_ip(request: Request) -> str:
    """
    鑾峰彇瀹㈡埛绔湡瀹?IP銆?
    瀹夊叏璇存槑锛?    - X-Forwarded-For / X-Real-IP 鍙瀹㈡埛绔吉閫狅紝鐩存帴淇′换浼氱粫杩囬€熺巼闄愬埗銆?    - 鍙湁鍦ㄧ‘璁よ姹傜粡杩囧彲淇″弽鍚戜唬鐞嗭紙Nginx/CDN锛夋椂鎵嶈鍙栬繖浜涘ご閮ㄣ€?    - 閫氳繃鐜鍙橀噺 TRUST_PROXY=true 鏄惧紡寮€鍚紝榛樿鍏抽棴锛堢洿鎺ュ彇 TCP 杩炴帴 IP锛夈€?    """
    import os
    trust_proxy = os.getenv("TRUST_PROXY", "false").lower() in ("true", "1", "yes")

    if trust_proxy:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 鍙栫涓€涓?IP锛堟渶宸︿晶涓哄鎴风鐪熷疄 IP锛?            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

    # 榛樿锛氱洿鎺ヤ娇鐢?TCP 杩炴帴鐨勫绔?IP锛屼笉鍙吉閫?    return request.client.host if request.client else "unknown"


# 鈹€鈹€ 鐭俊鍙戦€?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def _send_sms(phone: str, code: str) -> bool:
    """
    鍙戦€佺煭淇￠獙璇佺爜銆?    鏀寔闃块噷浜慡MS鍜岃吘璁簯SMS锛岄€氳繃鐜鍙橀噺 SMS_PROVIDER 鍒囨崲銆?    鏈厤缃椂杩斿洖 False锛圖EBUG 妯″紡涓嬩笉褰卞搷鍔熻兘锛夈€?
    鐜鍙橀噺閰嶇疆绀轰緥锛坆ackend/.env锛夛細
      # 闃块噷浜?      SMS_PROVIDER=aliyun
      SMS_ACCESS_KEY=your_access_key_id
      SMS_SECRET_KEY=your_access_key_secret
      SMS_SIGN_NAME=鎮﹁灏忕伅濉?      SMS_TEMPLATE_CODE=SMS_xxxxxxxxx

      # 鑵捐浜?      SMS_PROVIDER=tencent
      SMS_ACCESS_KEY=your_secret_id
      SMS_SECRET_KEY=your_secret_key
      SMS_APP_ID=your_sms_app_id
      SMS_SIGN_NAME=鎮﹁灏忕伅濉?      SMS_TEMPLATE_CODE=your_template_id
    """
    provider = getattr(settings, 'SMS_PROVIDER', '') or ''
    access_key = getattr(settings, 'SMS_ACCESS_KEY', '') or ''
    secret_key = getattr(settings, 'SMS_SECRET_KEY', '') or ''
    sign_name = getattr(settings, 'SMS_SIGN_NAME', '鎮﹁灏忕伅濉?) or '鎮﹁灏忕伅濉?
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
        # 涓嶅湪鏃ュ織涓墦鍗板畬鏁村紓甯革紝閬垮厤娉勯湶 key
        logger.error(f"SMS send failed: {type(e).__name__}")
        return False


def _send_aliyun_sms(phone, code, access_key, secret_key, sign_name, template_code) -> bool:
    """闃块噷浜戠煭淇″彂閫侊紙闇€瀹夎 alibabacloud-dysmsapi20170525锛?""
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
    """鑵捐浜戠煭淇″彂閫侊紙闇€瀹夎 tencentcloud-sdk-python-sms锛?""
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


# 鈹€鈹€ 楠岃瘉鐮佹搷浣滐紙绾跨▼瀹夊叏锛?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def _get_code(phone: str):
    """绾跨▼瀹夊叏鍦拌幏鍙栭獙璇佺爜鏉＄洰"""
    with _codes_lock:
        return verification_codes.get(phone)


def _set_code(phone: str, code: str):
    """绾跨▼瀹夊叏鍦拌缃獙璇佺爜"""
    with _codes_lock:
        verification_codes[phone] = {
            "code": code,
            "expires_at": time.time() + CODE_EXPIRE_SECONDS,
            "attempts": 0,
        }


def _delete_code(phone: str):
    """绾跨▼瀹夊叏鍦板垹闄ら獙璇佺爜"""
    with _codes_lock:
        verification_codes.pop(phone, None)


def _validate_code(phone: str, code: str) -> tuple[bool, str]:
    """
    楠岃瘉楠岃瘉鐮侊紝杩斿洖 (is_valid, error_message)銆?    楠岃瘉鎴愬姛鍚庤嚜鍔ㄥ垹闄ら獙璇佺爜锛堟秷鑰楀瀷锛夈€?    瓒呰繃鏈€澶у皾璇曟鏁板悗鑷姩浣滃簾銆?    """
    with _codes_lock:
        entry = verification_codes.get(phone)
        if not entry:
            return False, "楠岃瘉鐮佷笉瀛樺湪鎴栧凡杩囨湡"
        if time.time() > entry["expires_at"]:
            verification_codes.pop(phone, None)
            return False, "楠岃瘉鐮佸凡杩囨湡锛岃閲嶆柊鑾峰彇"
        # 灏濊瘯娆℃暟闄愬埗
        if entry.get("attempts", 0) >= MAX_CODE_ATTEMPTS:
            verification_codes.pop(phone, None)
            return False, "楠岃瘉鐮佸凡澶辨晥锛岃閲嶆柊鑾峰彇"
        if entry["code"] != code:
            entry["attempts"] = entry.get("attempts", 0) + 1
            return False, "楠岃瘉鐮侀敊璇?
        # 楠岃瘉鎴愬姛锛屾秷鑰楅獙璇佺爜
        verification_codes.pop(phone, None)
        return True, ""


# 鈹€鈹€ 璇锋眰浣撴ā鍨?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

class PhoneRequest(BaseModel):
    phone: str


class LoginByCodeRequest(BaseModel):
    phone: str
    code: str


# 鈹€鈹€ 娉ㄥ唽 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.post("/register", response_model=Token)
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new parent user"""
    # IP 绾у埆閫熺巼闄愬埗锛氭瘡涓?IP 姣忓皬鏃舵渶澶氭敞鍐?10 娆?    ip = _get_client_ip(request)
    if not _check_rate_limit(f"register:{ip}", max_calls=10, window_seconds=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="娉ㄥ唽璇锋眰杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯"
        )

    # 鎵嬫満鍙锋敞鍐屾椂蹇呴』楠岃瘉楠岃瘉鐮侊紱绾敤鎴峰悕娉ㄥ唽锛堟棤鎵嬫満鍙凤級鍒欒烦杩?    if user_data.phone:
        if not user_data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="鎵嬫満鍙锋敞鍐屽繀椤绘彁渚涢獙璇佺爜"
            )
        valid, err = _validate_code(user_data.phone, user_data.code)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    if user_data.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="鐢ㄦ埛鍚嶅凡琚敞鍐?
            )

    # 鎵嬫満鍙峰敮涓€鎬ф鏌?    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="璇ユ墜鏈哄彿宸叉敞鍐?
            )

    final_username = user_data.username or user_data.phone
    if not final_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="璇锋彁渚涚敤鎴峰悕鎴栨墜鏈哄彿")

    user = User(
        username=final_username,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 澶勭悊閭€璇风爜锛堝彲閫夛紝澶辫触涓嶅奖鍝嶆敞鍐岋級
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
            logger.warning(f"澶勭悊閭€璇风爜澶辫触锛堜笉褰卞搷娉ㄥ唽锛? {e}")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# 鈹€鈹€ 瀵嗙爜鐧诲綍 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.post("/login", response_model=Token)
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with username/phone and password"""
    # IP 绾у埆閫熺巼闄愬埗锛氭瘡涓?IP 姣忓垎閽熸渶澶?10 娆★紝姣忓皬鏃舵渶澶?30 娆?    ip = _get_client_ip(request)
    if not _check_rate_limit(f"login_min:{ip}", max_calls=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="鐧诲綍灏濊瘯杩囦簬棰戠箒锛岃1鍒嗛挓鍚庡啀璇?
        )
    if not _check_rate_limit(f"login_hr:{ip}", max_calls=30, window_seconds=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="鐧诲綍灏濊瘯杩囦簬棰戠箒锛岃1灏忔椂鍚庡啀璇?
        )

    # 鏀寔鐢ㄦ埛鍚嶆垨鎵嬫満鍙风櫥褰?    user = db.query(User).filter(
        (User.username == user_data.username) | (User.phone == user_data.username)
    ).first()

    # 缁熶竴閿欒淇℃伅锛岄槻姝㈢敤鎴锋灇涓?    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="璐﹀彿鎴栧瘑鐮侀敊璇?
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# 鈹€鈹€ 楠岃瘉鐮佺櫥褰?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.post("/login-by-code", response_model=Token)
def login_by_code(request: Request, data: LoginByCodeRequest, db: Session = Depends(get_db)):
    """Login with phone + verification code (auto-register if not exists)"""
    # IP 绾у埆閫熺巼闄愬埗
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"login_code:{ip}", max_calls=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="璇锋眰杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯"
        )

    valid, err = _validate_code(data.phone, data.code)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    # 鏌ユ壘鎴栬嚜鍔ㄦ敞鍐?    user = db.query(User).filter(User.phone == data.phone).first()
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


# 鈹€鈹€ 褰撳墠鐢ㄦ埛淇℃伅 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return UserResponse.model_validate(current_user)


# 鈹€鈹€ 鍙戦€侀獙璇佺爜 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.post("/send-code")
def send_verification_code(request: Request, req_body: PhoneRequest):
    """Send verification code to phone"""
    phone = req_body.phone

    # 鎵嬫満鍙锋牸寮忔牎楠岋紙鏇翠弗鏍肩殑姝ｅ垯锛?    if not re.match(r'^1[3-9]\d{9}$', phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="鎵嬫満鍙锋牸寮忎笉姝ｇ‘"
        )

    # IP 绾у埆閫熺巼闄愬埗锛氭瘡涓?IP 姣忓垎閽熸渶澶?5 娆?    ip = _get_client_ip(request)
    if not _check_rate_limit(f"send_code_ip:{ip}", max_calls=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="璇锋眰杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯"
        )

    # 鎵嬫満鍙风骇鍒細60绉掑唴涓嶈兘閲嶅鍙戦€?    entry = _get_code(phone)
    if entry and time.time() < entry["expires_at"] - CODE_EXPIRE_SECONDS + 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="鍙戦€佸お棰戠箒锛岃60绉掑悗鍐嶈瘯"
        )

    # 浣跨敤 secrets 妯″潡鐢熸垚瀵嗙爜瀛﹀畨鍏ㄧ殑闅忔満楠岃瘉鐮?    import secrets as _secrets
    code = ''.join([str(_secrets.randbelow(10)) for _ in range(4)])
    _set_code(phone, code)

    # 灏濊瘯鍙戦€佺湡瀹炵煭淇★紙闇€閰嶇疆 SMS_PROVIDER / SMS_ACCESS_KEY / SMS_SECRET_KEY锛?    sms_sent = _send_sms(phone, code)

    # DEBUG 妯″紡涓嬪缁堟墦鍗板埌鏃ュ織锛堟柟渚垮紑鍙戣皟璇曪級
    if settings.DEBUG:
        logger.debug(f"[DEV] 楠岃瘉鐮佸凡鐢熸垚锛屾墜鏈哄彿鏈?浣? ...{phone[-4:]}锛岄獙璇佺爜: {code}锛坽CODE_EXPIRE_SECONDS}绉掑唴鏈夋晥锛?)
    elif not sms_sent:
        # 鐢熶骇鐜涓旂煭淇″彂閫佸け璐ユ椂锛岃繑鍥為敊璇?        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="鐭俊鍙戦€佸け璐ワ紝璇风◢鍚庨噸璇?
        )

    return {"message": "楠岃瘉鐮佸凡鍙戦€?, "expires_in": CODE_EXPIRE_SECONDS}


# 鈹€鈹€ 璐﹀彿淇℃伅缂栬緫 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    phone_code: Optional[str] = None  # 淇敼鎵嬫満鍙锋椂闇€瑕侀獙璇佺爜


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """淇敼鐢ㄦ埛鍚嶆垨鎵嬫満鍙?""
    if data.username and data.username != current_user.username:
        # 鐢ㄦ埛鍚嶉暱搴﹂檺鍒?        if len(data.username) > 50:
            raise HTTPException(status_code=400, detail="鐢ㄦ埛鍚嶄笉鑳借秴杩?0涓瓧绗?)
        existing = db.query(User).filter(
            User.username == data.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="鐢ㄦ埛鍚嶅凡琚崰鐢?)
        current_user.username = data.username

    if data.phone and data.phone != current_user.phone:
        # 鎵嬫満鍙锋牸寮忔牎楠?        if not re.match(r'^1[3-9]\d{9}$', data.phone):
            raise HTTPException(status_code=400, detail="鎵嬫満鍙锋牸寮忎笉姝ｇ‘")
        # 淇敼鎵嬫満鍙烽渶瑕侀獙璇佺爜
        if not data.phone_code:
            raise HTTPException(status_code=400, detail="淇敼鎵嬫満鍙烽渶瑕佹彁渚涢獙璇佺爜")
        valid, err = _validate_code(data.phone, data.phone_code)
        if not valid:
            raise HTTPException(status_code=400, detail=err)
        existing = db.query(User).filter(
            User.phone == data.phone,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="璇ユ墜鏈哄彿宸茶鍏朵粬璐﹀彿缁戝畾")
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
    """淇敼瀵嗙爜"""
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="鍘熷瘑鐮侀敊璇?)
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="鏂板瘑鐮侀暱搴︿笉鑳藉皯浜?浣?)
    if len(data.new_password) > 128:
        raise HTTPException(status_code=400, detail="鏂板瘑鐮佷笉鑳借秴杩?28浣?)
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "瀵嗙爜淇敼鎴愬姛"}


# 鈹€鈹€ 鍎跨妯″紡閫€鍑哄瘑鐮侀獙璇?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

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
    楠岃瘉褰撳墠鐧诲綍鐢ㄦ埛鐨勫瘑鐮侊紙鐢ㄤ簬鍎跨妯″紡閫€鍑洪獙璇侊級銆?    涓嶉鍙戞柊 token锛屼粎杩斿洖楠岃瘉缁撴灉銆?    涓?/login 涓嶅悓锛屾鎺ュ彛闇€瑕佹惡甯︽湁鏁?JWT锛屼笉浼氳Е鍙戝叏灞€鐧诲嚭鎷︽埅鍣ㄣ€?    """
    # IP 绾у埆閫熺巼闄愬埗锛氭瘡鍒嗛挓鏈€澶?10 娆★紝闃叉鏆村姏鐮磋В
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"verify_pwd:{ip}", max_calls=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="楠岃瘉杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯"
        )

    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="瀵嗙爜閿欒"
        )

    return {"valid": True}


# 鈹€鈹€ 寰俊灏忕▼搴忕櫥褰?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

class WxLoginRequest(BaseModel):
    code: str  # wx.login() 杩斿洖鐨?code
    guest_id: Optional[str] = None  # 娓稿 ID锛岀敤浜庢暟鎹縼绉?

def migrate_guest_data(guest_id: str, user_id: int, db: Session) -> int:
    """
    灏嗘父瀹㈢瓫鏌ヨ褰曡縼绉诲埌宸茬櫥褰曠敤鎴枫€?
    瀹夊叏璇存槑锛?    - guest_id 鐢卞鎴风浼犲叆锛屼笉鑳界洿鎺ヤ俊浠汇€?    - 杩佺Щ鍚庡皢 child_id 璁剧疆涓鸿鐢ㄦ埛鍚嶄笅鐨勭涓€涓瀛愶紙濡傛湁锛夛紝
      骞舵竻绌?guest_id 闃叉閲嶅杩佺Щ锛堝箓绛夛級銆?    - 涓嶉獙璇?guest_id 褰掑睘锛堟父瀹㈡棤璐﹀彿锛屾棤娉曞仛褰掑睘楠岃瘉锛夛紝
      浣嗛€氳繃"娓呯┖鍚庝笉鍙啀杩佺Щ"淇濊瘉姣忔潯璁板綍鍙兘琚縼绉讳竴娆°€?    """
    from ..models.screening import Screening
    from ..models.child import Child

    # 鏌ユ壘璇ョ敤鎴峰悕涓嬬殑绗竴涓瀛愶紙鐢ㄤ簬鍏宠仈杩佺Щ鐨勭瓫鏌ヨ褰曪級
    child = db.query(Child).filter(Child.parent_id == user_id).first()

    screenings = db.query(Screening).filter(
        Screening.guest_id == guest_id
    ).all()

    count = len(screenings)
    for screening in screenings:
        screening.guest_id = None  # 娓呯┖ guest_id锛岄槻姝㈤噸澶嶈縼绉?        # 濡傛灉璇ョ敤鎴峰凡鏈夊瀛愭。妗堬紝灏嗙瓫鏌ヨ褰曞叧鑱斿埌璇ュ瀛?        if child and screening.child_id is None:
            screening.child_id = child.id

    if count > 0:
        db.commit()

    return count


@router.post("/wx-login", response_model=Token)
async def wx_login(request: Request, data: WxLoginRequest, db: Session = Depends(get_db)):
    """
    寰俊灏忕▼搴忕櫥褰曘€?    1. 鐢?code 鎹㈠彇 openid锛堣皟鐢ㄥ井淇?jscode2session 鎺ュ彛锛?    2. 鐢?wechat_openid 瀛楁鏌ユ壘鎴栧垱寤虹敤鎴?    3. 鑻ヤ紶鍏?guest_id锛岃縼绉绘父瀹㈡暟鎹?    4. 杩斿洖 JWT token 鍙婅縼绉绘暟閲?    """
    import httpx

    # IP 閫熺巼闄愬埗
    ip = _get_client_ip(request)
    if not _check_rate_limit(f"wx_login:{ip}", max_calls=20, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="璇锋眰杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯"
        )

    wx_appid = getattr(settings, "WX_APPID", "")
    wx_secret = getattr(settings, "WX_SECRET", "")

    if not wx_appid or not wx_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="寰俊鐧诲綍鏈厤缃紝璇峰湪 .env 涓缃?WX_APPID 鍜?WX_SECRET"
        )

    # 璋冪敤寰俊 jscode2session
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
            detail="寰俊鏈嶅姟璇锋眰澶辫触锛岃绋嶅悗閲嶈瘯"
        )

    if "errcode" in wx_data and wx_data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"寰俊鐧诲綍澶辫触: {wx_data.get('errmsg', '鏈煡閿欒')}"
        )

    openid = wx_data.get("openid")
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="鏃犳硶鑾峰彇寰俊 openid"
        )

    # 鐢?wechat_openid 瀛楁鏌ユ壘鐢ㄦ埛锛堝吋瀹规棫鐨?username=wx_{openid} 鏂瑰紡锛?    user = db.query(User).filter(User.wechat_openid == openid).first()

    # 鍏煎鏃ф暟鎹細灏濊瘯閫氳繃鏃?username 鏍煎紡鏌ユ壘骞跺崌绾?    if not user:
        old_username = f"wx_{openid}"
        user = db.query(User).filter(User.username == old_username).first()
        if user:
            # 鍗囩骇鏃х敤鎴凤細鍐欏叆 wechat_openid 瀛楁
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

    # 娓稿鏁版嵁杩佺Щ
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


# 鈹€鈹€ 娓稿鐧诲綍 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.post("/guest-login", response_model=Token)
def guest_login(request: Request, db: Session = Depends(get_db)):
    """
    娓稿涓€閿繘鍏ョ郴缁熴€?    鑷姩鍒涘缓涓€涓复鏃舵父瀹㈣处鍙凤紙username=guest_xxxxxxxx锛夛紝杩斿洖鏈夋晥鏈?澶╃殑JWT銆?    娓稿璐﹀彿鍙互姝ｅ父浣跨敤绯荤粺鎵€鏈夊姛鑳斤紝娉ㄥ唽鍚庡彲鍗囩骇涓烘寮忚处鍙枫€?    """
    import secrets as _secrets

    # IP 閫熺巼闄愬埗锛氭瘡IP姣忓皬鏃舵渶澶氬垱寤?0涓父瀹㈣处鍙?    ip = _get_client_ip(request)
    if not _check_rate_limit(f"guest_login:{ip}", max_calls=10, window_seconds=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="璇锋眰杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯"
        )

    # 鐢熸垚鍞竴娓稿鐢ㄦ埛鍚?    for _ in range(5):
        suffix = _secrets.token_hex(4)  # 8浣嶉殢鏈篽ex
        username = f"guest_{suffix}"
        if not db.query(User).filter(User.username == username).first():
            break
    else:
        raise HTTPException(status_code=500, detail="鍒涘缓娓稿璐﹀彿澶辫触锛岃閲嶈瘯")

    user = User(
        username=username,
        password_hash=get_password_hash(_secrets.token_hex(32)),
        phone=None,
        is_guest=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7)
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


# 鈹€鈹€ 閭€璇风爜绯荤粺 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@router.get("/invite-code")
def get_invite_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """鑾峰彇褰撳墠鐢ㄦ埛鐨勯個璇风爜锛堜笉瀛樺湪鍒欑敓鎴愶級"""
    import secrets as _secrets
    from ..models.invite import InviteRecord

    # 鏌ユ壘宸叉湁閭€璇风爜
    existing = db.query(InviteRecord).filter(
        InviteRecord.inviter_id == current_user.id,
        InviteRecord.invitee_id == None,  # noqa: E711
    ).first()

    if existing:
        return {"invite_code": existing.invite_code}

    # 浣跨敤 secrets 鐢熸垚瀵嗙爜瀛﹀畨鍏ㄧ殑閭€璇风爜锛?浣嶅ぇ鍐欏瓧姣?鏁板瓧锛?    # secrets.token_hex 鐢熸垚鐨勫瓧绗﹂泦涓?0-9a-f锛岃浆澶у啓鍚庡彇鍓?浣?    for _ in range(10):  # 鏈€澶氶噸璇?0娆￠伩鍏嶇鎾?        code = _secrets.token_hex(6).upper()[:8]  # 12浣峢ex鍙栧墠8浣嶏紝瀛楃闆嗚冻澶?        if not db.query(InviteRecord).filter(InviteRecord.invite_code == code).first():
            record = InviteRecord(
                inviter_id=current_user.id,
                invite_code=code,
            )
            db.add(record)
            db.commit()
            return {"invite_code": code}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="鐢熸垚閭€璇风爜澶辫触锛岃閲嶈瘯"
    )
