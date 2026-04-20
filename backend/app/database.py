from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# SQLite specific: check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
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
    from .models import user, child, screening, training, ai_chat, reward
    # 导入通知模块的模型，确保表被创建
    from .api import notifications as notif_module  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # ── 轻量级字段迁移（SQLite 不支持 ALTER COLUMN，只能 ADD COLUMN）──────────
    # 每次启动时检查并补全缺失字段，幂等安全
    _ensure_columns = [
        ("training_tasks", "correct_count", "INTEGER"),
        ("training_tasks", "total_count",   "INTEGER"),
        ("training_tasks", "accuracy",      "INTEGER"),
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
