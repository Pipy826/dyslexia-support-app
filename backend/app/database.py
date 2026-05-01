from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# SQLite specific: check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# PostgreSQL 不支持 charset 参数（它通过连接字符串或 client_encoding 配置）
# MySQL 需要 charset 参数
if "mysql" in settings.DATABASE_URL.lower():
    connect_args["charset"] = "utf8mb4"

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # 连接池预检查，避免断连
    # 连接池配置（SQLite 不支持多连接池，PostgreSQL/MySQL 生效）
    **({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # 30分钟回收连接，防止数据库断开
    } if "sqlite" not in settings.DATABASE_URL else {})
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables, and apply lightweight column migrations for SQLite."""
    from .models import user, child, screening, training, ai_chat, reward, invite, notification, article
    # 导入通知模块的模型，确保 push_tokens / notifications 表被创建
    from .api import notifications as notif_module  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # ── 轻量级字段迁移（SQLite 不支持 ALTER COLUMN，只能 ADD COLUMN）──────────
    # 每次启动时检查并补全缺失字段，幂等安全
    _ensure_columns = [
        # training_tasks 新增字段
        ("training_tasks", "correct_count", "INTEGER"),
        ("training_tasks", "total_count",   "INTEGER"),
        ("training_tasks", "accuracy",      "INTEGER"),
        # children 连续打卡字段（后续版本新增）
        ("children", "current_streak",    "INTEGER NOT NULL DEFAULT 0"),
        ("children", "longest_streak",    "INTEGER NOT NULL DEFAULT 0"),
        ("children", "last_activity_date","DATE"),
        # users 微信登录字段
        ("users", "wechat_openid", "VARCHAR(64)"),
        # screenings 游客数据迁移字段
        ("screenings", "guest_id", "VARCHAR(64)"),
        # articles 表字段（Enum 改 String 后需要补列）
        ("articles", "content_type", "VARCHAR(20) NOT NULL DEFAULT 'article'"),
        ("articles", "title",        "VARCHAR(200)"),
        ("articles", "summary",      "VARCHAR(500)"),
        ("articles", "content",      "TEXT"),
        ("articles", "cover_image",  "VARCHAR(500)"),
        ("articles", "video_url",    "VARCHAR(500)"),
        ("articles", "tags",         "VARCHAR(300)"),
        ("articles", "author",       "VARCHAR(100) DEFAULT '星萌乐学'"),
        ("articles", "is_published", "INTEGER NOT NULL DEFAULT 1"),
        ("articles", "is_featured",  "INTEGER NOT NULL DEFAULT 0"),
        ("articles", "view_count",   "INTEGER NOT NULL DEFAULT 0"),
    ]
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    with engine.connect() as conn:
        for table, col, col_type in _ensure_columns:
            if table not in existing_tables:
                continue
            existing_cols = [c["name"] for c in inspector.get_columns(table)]
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
        conn.commit()
