import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse

from ..config import settings
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _ensure_upload_dir():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传头像，返回可访问的URL"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：{file.content_type}，请上传 JPG/PNG/GIF/WebP 图片"
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )

    _ensure_upload_dir()

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/api/upload/files/{filename}"
    return {"url": url, "filename": filename}


@router.get("/files/{filename}")
async def get_file(filename: str):
    """获取上传的文件"""
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    # 防止路径穿越
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="非法文件名")
    return FileResponse(filepath)
