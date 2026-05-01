from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import os
import logging

from .database import init_db
from .api import auth, children, screenings, reports, training, ai_qa, upload, notifications, articles
from .config import settings
from .scheduler import start_scheduler, stop_scheduler

# 日志配置
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 请求体大小限制（10MB，防止 DoS）
MAX_REQUEST_BODY_SIZE = 10 * 1024 * 1024  # 10MB


# 确保 JSON 响应使用 UTF-8 编码
class UTF8JSONResponse(JSONResponse):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("media_type", "application/json; charset=utf-8")
        super().__init__(*args, **kwargs)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """限制请求体大小，防止超大请求导致 DoS"""
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "请求体过大，最大支持 10MB"}
            )
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全响应头，防止常见 Web 攻击"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # 防止 MIME 类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"
        # 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"
        # XSS 保护（旧浏览器）
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # 不在 Referer 中泄露路径
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # 生产环境启用 HSTS
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理（替代已废弃的 on_event）"""
    # 启动
    logger.info(f"Starting {settings.APP_NAME} ...")
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Database initialized.")
    start_scheduler()
    yield
    # 关闭
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    description="儿童读写障碍智能筛查与干预系统 API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,   # 生产环境关闭 Swagger
    redoc_url="/redoc" if settings.DEBUG else None,
    default_response_class=UTF8JSONResponse,
    lifespan=lifespan,
)

# 中间件注册顺序：后注册的先执行
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

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

# Register routers
app.include_router(auth.router)
app.include_router(children.router)
app.include_router(screenings.router)
app.include_router(reports.router)
app.include_router(training.router)
app.include_router(ai_qa.router)
app.include_router(upload.router)
app.include_router(notifications.router)
app.include_router(articles.router)

# 静态文件服务：挂载上传目录，使头像等文件可通过 /uploads/ 直接访问
# 注意：必须在 upload.router 注册之后挂载，避免路由冲突
# 目录在 startup 事件中创建，这里确保挂载前目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="static_uploads")


@app.get("/")
def root():
    return {"message": "儿童读写障碍筛查系统 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
