import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse

from ..config import settings
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# content_type → 安全扩展名映射，避免使用用户提供的文件名扩展名
_EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png":  "png",
    "image/gif":  "gif",
    "image/webp": "webp",
}

# 各格式的 magic bytes（文件头签名）
# 用于验证实际文件内容，防止伪装的恶意文件
_MAGIC_BYTES: dict[str, list[bytes]] = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png":  [b"\x89PNG\r\n\x1a\n"],
    "image/gif":  [b"GIF87a", b"GIF89a"],
    "image/webp": [b"RIFF"],  # RIFF....WEBP，前4字节即可
}


def _verify_magic_bytes(content: bytes, content_type: str) -> bool:
    """
    验证文件内容的 magic bytes 是否与声明的 content_type 一致。
    防止攻击者将恶意文件伪装成图片上传。
    """
    signatures = _MAGIC_BYTES.get(content_type, [])
    if not signatures:
        return False
    return any(content.startswith(sig) for sig in signatures)


def _ensure_upload_dir():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def _safe_filename(filename: str) -> bool:
    """
    检查文件名是否安全（防路径穿越）。
    拒绝包含路径分隔符、空字节、或以点开头的文件名。
    """
    if not filename:
        return False
    # 拒绝路径分隔符、空字节、控制字符
    forbidden = ['..', '/', '\\', '\x00', '\r', '\n']
    for f in forbidden:
        if f in filename:
            return False
    # 拒绝以点开头（隐藏文件）
    if filename.startswith('.'):
        return False
    return True


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传头像，返回可访问的URL"""
    # 1. 检查声明的 MIME 类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，请上传 JPG/PNG/GIF/WebP 图片"
        )

    content = await file.read()

    # 2. 检查文件大小
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )

    # 3. 验证 magic bytes（防止伪装文件）
    if not _verify_magic_bytes(content, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件内容与声明类型不符，请上传真实的图片文件"
        )

    _ensure_upload_dir()

    # 4. 扩展名由 content_type 决定，不信任用户提供的文件名
    ext = _EXT_MAP.get(file.content_type, "jpg")
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    # 5. 二次确认路径安全（防止 UPLOAD_DIR 配置异常导致的路径穿越）
    upload_dir_abs = os.path.realpath(settings.UPLOAD_DIR)
    filepath_abs = os.path.realpath(filepath)
    if not filepath_abs.startswith(upload_dir_abs + os.sep):
        raise HTTPException(status_code=400, detail="非法文件路径")

    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/api/upload/files/{filename}"
    return {"url": url, "filename": filename}


@router.get("/files/{filename}")
async def get_file(filename: str):
    """获取上传的文件"""
    # 路径穿越检查：必须在文件系统操作之前
    if not _safe_filename(filename):
        raise HTTPException(status_code=400, detail="非法文件名")

    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    # 二次确认：realpath 解析后仍在上传目录内
    upload_dir_abs = os.path.realpath(settings.UPLOAD_DIR)
    filepath_abs = os.path.realpath(filepath)
    if not filepath_abs.startswith(upload_dir_abs + os.sep):
        raise HTTPException(status_code=400, detail="非法文件路径")

    if not os.path.exists(filepath_abs):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(filepath_abs)
