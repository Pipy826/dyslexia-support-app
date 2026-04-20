"""
pytest 配置文件：设置测试数据库和 TestClient
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test_integration.db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """直接 patch app.database 的 engine 和 SessionLocal"""
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # 导入所有模型，确保 Base.metadata 包含所有表
    import app.database as db_module
    from app.models import user, child, screening, training, ai_chat, reward  # noqa
    from app.api import notifications  # noqa

    # 建表
    db_module.Base.metadata.create_all(bind=test_engine)

    # Patch engine 和 SessionLocal
    original_engine = db_module.engine
    original_session_local = db_module.SessionLocal
    db_module.engine = test_engine
    db_module.SessionLocal = TestSessionLocal

    # Patch init_db（避免 startup 里重新建表/迁移）
    original_init_db = db_module.init_db
    db_module.init_db = lambda: None

    # Patch app.main 里的 init_db 引用
    import app.main as main_module
    main_module.init_db = lambda: None

    yield

    # 恢复
    db_module.engine = original_engine
    db_module.SessionLocal = original_session_local
    db_module.init_db = original_init_db
    main_module.init_db = original_init_db

    # 清理测试 DB
    test_engine.dispose()
    db_path = TEST_DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass


@pytest.fixture(scope="session")
def client(setup_test_db):
    from app.main import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
