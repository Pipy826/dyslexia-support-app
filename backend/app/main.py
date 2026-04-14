from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

from .database import init_db
from .api import auth, children, screenings, reports, training, ai_qa, upload
from .config import settings

# 日志配置
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="儿童读写障碍智能筛查与干预系统 API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,   # 生产环境关闭 Swagger
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS：开发环境允许所有来源，生产环境通过 ALLOWED_ORIGINS 配置
_origins = settings.allowed_origins_list if settings.allowed_origins_list else (["*"] if settings.DEBUG else [])
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"}
    )

# Initialize database on startup
@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.APP_NAME} ...")
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Database initialized.")

# Register routers
app.include_router(auth.router)
app.include_router(children.router)
app.include_router(screenings.router)
app.include_router(reports.router)
app.include_router(training.router)
app.include_router(ai_qa.router)
app.include_router(upload.router)


@app.get("/")
def root():
    return {"message": "儿童读写障碍筛查系统 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
