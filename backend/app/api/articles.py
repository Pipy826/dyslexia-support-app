"""
科普文章/视频 API
- GET  /api/articles          获取文章列表（公开，无需认证）
- GET  /api/articles/{id}     获取文章详情（公开，无需认证，同时增加浏览量）
- POST /api/articles          发布文章（需认证，管理员用）
- PUT  /api/articles/{id}     更新文章（需认证）
- DELETE /api/articles/{id}   删除文章（需认证）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.article import Article
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/articles", tags=["科普文章"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class ArticleCreate(BaseModel):
    content_type: str = "article"   # article | video
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    video_url: Optional[str] = None
    tags: Optional[str] = None
    author: Optional[str] = "星萌乐学"
    is_published: bool = True
    is_featured: bool = False


class ArticleUpdate(BaseModel):
    content_type: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    video_url: Optional[str] = None
    tags: Optional[str] = None
    author: Optional[str] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None


def _to_dict(article: Article) -> dict:
    return {
        "id": article.id,
        "content_type": article.content_type,
        "title": article.title,
        "summary": article.summary,
        "content": article.content,
        "cover_image": article.cover_image,
        "video_url": article.video_url,
        "tags": article.tags.split(",") if article.tags else [],
        "author": article.author,
        "is_published": article.is_published,
        "is_featured": article.is_featured,
        "view_count": article.view_count,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
    }


# ── 公开接口（无需认证）──────────────────────────────────────────────────────

@router.get("")
def list_articles(
    content_type: Optional[str] = None,   # article | video | None（全部）
    tag: Optional[str] = None,            # 按标签筛选
    featured_only: bool = False,          # 只看推荐
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """获取科普文章/视频列表（公开）"""
    query = db.query(Article).filter(Article.is_published == True)

    if content_type in ("article", "video"):
        query = query.filter(Article.content_type == content_type)

    if tag:
        query = query.filter(Article.tags.contains(tag))

    if featured_only:
        query = query.filter(Article.is_featured == True)

    total = query.count()
    items = (
        query
        .order_by(Article.is_featured.desc(), Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_to_dict(a) for a in items],
    }


@router.get("/{article_id}")
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    """获取文章详情，同时增加浏览量（公开）"""
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.is_published == True,
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 增加浏览量
    article.view_count = (article.view_count or 0) + 1
    db.commit()

    return _to_dict(article)


# ── 管理接口（需认证）────────────────────────────────────────────────────────

@router.post("")
def create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发布文章（需登录）"""
    article = Article(
        content_type=data.content_type,
        title=data.title,
        summary=data.summary,
        content=data.content,
        cover_image=data.cover_image,
        video_url=data.video_url,
        tags=",".join(data.tags) if isinstance(data.tags, list) else data.tags,
        author=data.author or current_user.username,
        is_published=data.is_published,
        is_featured=data.is_featured,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return _to_dict(article)


@router.put("/{article_id}")
def update_article(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新文章（需登录）"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    for field, value in data.model_dump(exclude_none=True).items():
        if field == "tags" and isinstance(value, list):
            value = ",".join(value)
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return _to_dict(article)


@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除文章（需登录）"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    db.delete(article)
    db.commit()
    return {"message": "已删除"}
