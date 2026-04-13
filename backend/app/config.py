from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "儿童读写障碍筛查系统"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./dyslexia.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI 配置（兼容 OpenAI 格式，可接入 OpenAI / DeepSeek / 通义千问等）
    # 在 backend/.env 中配置：
    #   AI_API_KEY=sk-xxxx
    #   AI_API_BASE_URL=https://api.openai.com/v1
    #   AI_MODEL=gpt-4o-mini
    AI_API_KEY: str = ""
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
