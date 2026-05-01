"""
科普文章/视频模型
支持图文和视频两种类型，管理员可在后台发布，公众可浏览分享
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    # 内容类型：article=图文，video=视频
    content_type = Column(String(20), nullable=False, default="article")

    title = Column(String(200), nullable=False)
    summary = Column(String(500), nullable=True)   # 摘要/简介
    content = Column(Text, nullable=True)           # 图文正文（Markdown 或纯文本）
    cover_image = Column(String(500), nullable=True)  # 封面图 URL
    video_url = Column(String(500), nullable=True)    # 视频链接（视频类型用）

    # 标签，逗号分隔，如 "读写障碍,家长指南,早期干预"
    tags = Column(String(300), nullable=True)

    # 作者/来源
    author = Column(String(100), nullable=True, default="星萌乐学")

    # 状态
    is_published = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)  # 是否置顶推荐

    # 统计
    view_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
