from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    APP_NAME: str = "儿童读写障碍筛查系统"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./dyslexia.db"

    # JWT — 生产环境必须在 .env 中设置随机长字符串
    # 生成命令：python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = "dev-only-secret-key-CHANGE-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # CORS — 生产环境填写前端域名，多个用逗号分隔
    # 例：ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
    # 留空时：DEBUG=True 允许所有来源，DEBUG=False 拒绝所有跨域
    ALLOWED_ORIGINS: str = ""

    # AI 配置（兼容 OpenAI 格式）
    # 支持 OpenAI / DeepSeek / 通义千问 / NVIDIA 等
    # 根据 API_KEY 的前缀自动识别服务商：
    #   sk- 开头 → OpenAI
    #   nvapi- 开头 → NVIDIA
    #   ds- 开头 → DeepSeek
    #   其他 → 默认 OpenAI 兼容格式
    AI_API_KEY: str = ""
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"

    @field_validator("AI_API_BASE_URL", "AI_MODEL", mode="before")
    @classmethod
    def auto_detect_ai_provider(cls, v: str, info) -> str:
        # 获取已设置的 API_KEY（通过 info.data 获取）
        api_key = info.data.get('AI_API_KEY', '') or ''
        
        # 如果没有 API_KEY，跳过自动检测
        if not api_key:
            return v
        
        # 根据 key 前缀自动设置 API 地址
        if api_key.startswith('nvapi-'):
            # NVIDIA NIM
            if 'openai' in v or v == "https://api.openai.com/v1":
                return "https://api.nvcf.nvidia.com/v1"
        elif api_key.startswith('ds-'):
            # DeepSeek
            if 'openai' in v or v == "https://api.openai.com/v1":
                return "https://api.deepseek.com/v1"
        elif api_key.startswith('sk-') and 'aliyuncs' not in v:
            # OpenAI（默认）
            if 'dashscope' in v or 'qwen' in v:
                return "https://api.openai.com/v1"
        
        return v

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # 微信小程序
    WX_APPID: str = ""
    WX_SECRET: str = ""

    # 专业咨询联系方式（显示在 AI 跳转提示中）
    CONTACT_PHONE: str = "0755-33941800"
    CONTACT_WECHAT: str = ""  # 可选：微信客服号

    # 短信服务（可选，不配置则 DEBUG 模式下打印到日志）
    # 支持 aliyun（阿里云）/ tencent（腾讯云）
    SMS_PROVIDER: str = ""
    SMS_ACCESS_KEY: str = ""
    SMS_SECRET_KEY: str = ""
    SMS_SIGN_NAME: str = "悦读小灯塔"
    SMS_TEMPLATE_CODE: str = ""
    SMS_APP_ID: str = ""  # 腾讯云专用

    @field_validator("SECRET_KEY")
    @classmethod
    def warn_default_secret(cls, v: str) -> str:
        if v == "dev-only-secret-key-CHANGE-IN-PRODUCTION":
            import warnings
            import os
            # 生产环境（DEBUG=False）时，拒绝使用默认密钥
            if not os.getenv("DEBUG", "True").lower() in ("true", "1", "yes"):
                raise ValueError(
                    "❌ 生产环境禁止使用默认 SECRET_KEY！\n"
                    "   请在 .env 中设置随机密钥：\n"
                    "   SECRET_KEY=$(python -c \"import secrets; print(secrets.token_hex(32))\")"
                )
            warnings.warn(
                "⚠️  SECRET_KEY 使用默认值，生产环境请在 .env 中设置随机密钥！\n"
                "   生成命令：python -c \"import secrets; print(secrets.token_hex(32))\"",
                stacklevel=2,
            )
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
