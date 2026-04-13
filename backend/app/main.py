from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import init_db
from .api import auth, children, screenings, reports, training, ai_qa, upload
from .config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="儿童读写障碍智能筛查与干预系统 API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

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
