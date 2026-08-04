"""
数据库模型定义
"""
import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Float, Boolean, JSON, Enum as SAEnum, Index,
)
from sqlalchemy.orm import relationship
import enum

from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"       # 管理员 - 全部权限
    EDITOR = "editor"     # 编辑 - 可添加/编辑产品
    VIEWER = "viewer"     # 观察者 - 只读浏览


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    display_name = Column(String(64), default="")
    phone = Column(String(20), default="")
    role = Column(SAEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    icon = Column(String(8), default="📦")  # emoji图标
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    description = Column(String(256), default="")

    # 自引用关系
    children = relationship("Category", backref="parent", remote_side=[id], lazy="selectin")
    products = relationship("Product", back_populates="category", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
            "description": self.description,
            "children": [c.to_dict() for c in self.children] if self.children else [],
            "product_count": self.products.count() if self.products else 0,
        }


class Source(Base):
    """抓取源配置 - 用户配置要抓取的目标网站"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    url = Column(String(512), nullable=False)
    scraper_type = Column(String(64), default="html")  # html / rss / api
    crawl_frequency_hours = Column(Integer, default=24)
    is_active = Column(Boolean, default=True)
    last_crawl_at = Column(DateTime, nullable=True)
    last_crawl_status = Column(String(32), default="pending")  # pending / success / failed
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="source", lazy="dynamic")
    crawl_logs = relationship("CrawlLog", back_populates="source", lazy="dynamic",
                              order_by="CrawlLog.started_at.desc()")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "scraper_type": self.scraper_type,
            "crawl_frequency_hours": self.crawl_frequency_hours,
            "is_active": self.is_active,
            "last_crawl_at": self.last_crawl_at.isoformat() if self.last_crawl_at else None,
            "last_crawl_status": self.last_crawl_status,
            "notes": self.notes,
            "product_count": self.products.count(),
        }


class Product(Base):
    """产品主表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False, index=True)
    description = Column(Text, default="")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    source_url = Column(String(1024), default="")  # 原始来源网址
    # 联系方式 JSON: {"phone":"","wechat":"","email":"","website":""}
    contact_info = Column(JSON, default=dict)
    # 位置信息: province, city, scenic_name
    location = Column(JSON, default=dict)
    invest_range = Column(String(64), default="")  # 投资金额区间，如"10-50万"
    price_range = Column(String(64), default="")   # 产品售价区间
    tags = Column(JSON, default=list)  # 标签列表
    view_count = Column(Integer, default=0)
    status = Column(String(16), default="active")  # active / pending_review / archived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    category = relationship("Category", back_populates="products")
    source = relationship("Source", back_populates="products")
    images = relationship("ProductImage", back_populates="product",
                          lazy="selectin", order_by="ProductImage.sort_order",
                          cascade="all, delete-orphan")
    videos = relationship("ProductVideo", back_populates="product",
                          lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self, include_relations=True):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "",
            "category_icon": self.category.icon if self.category else "📦",
            "source_id": self.source_id,
            "source_name": self.source.name if self.source else "",
            "source_url": self.source_url,
            "contact_info": self.contact_info or {},
            "location": self.location or {},
            "invest_range": self.invest_range,
            "price_range": self.price_range,
            "tags": self.tags or [],
            "view_count": self.view_count,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_relations:
            data["images"] = [img.to_dict() for img in (self.images or [])]
            data["videos"] = [v.to_dict() for v in (self.videos or [])]
        return data

    def to_summary(self):
        """列表摘要（不含详细图片视频列表，只含封面）"""
        cover = None
        if self.images:
            covers = [img for img in self.images if img.is_cover]
            cover = covers[0] if covers else self.images[0]
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description[:200] if self.description else "",
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "",
            "category_icon": self.category.icon if self.category else "📦",
            "cover_image": cover.to_dict() if cover else None,
            "location": self.location or {},
            "invest_range": self.invest_range,
            "tags": self.tags or [],
            "view_count": self.view_count,
            "image_count": len(self.images) if self.images else 0,
            "video_count": len(self.videos) if self.videos else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    __table_args__ = (
        Index("idx_products_source_url_hash", "source_url"),
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(1024), default="")       # 原始图片URL
    local_path = Column(String(512), default="") # 本地存储路径
    thumbnail_path = Column(String(512), default="")  # 缩略图路径
    alt_text = Column(String(256), default="")
    sort_order = Column(Integer, default=0)
    is_cover = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "url": self.url if self.url else f"/static/images/{self.local_path}",
            "local_path": self.local_path,
            "thumbnail_path": self.thumbnail_path,
            "alt_text": self.alt_text,
            "sort_order": self.sort_order,
            "is_cover": self.is_cover,
        }


class ProductVideo(Base):
    __tablename__ = "product_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(1024), nullable=False)
    platform = Column(String(32), default="other")  # bilibili / youtube / douyin / other
    embed_code = Column(Text, default="")  # iframe 嵌入代码
    thumbnail_url = Column(String(1024), default="")
    title = Column(String(256), default="")

    product = relationship("Product", back_populates="videos")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "url": self.url,
            "platform": self.platform,
            "embed_code": self.embed_code,
            "thumbnail_url": self.thumbnail_url,
            "title": self.title,
        }


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    status = Column(String(32), default="running")  # running / success / partial / failed
    items_found = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    error_msg = Column(Text, default="")
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    source = relationship("Source", back_populates="crawl_logs")

    def to_dict(self):
        duration = None
        if self.finished_at and self.started_at:
            duration = (self.finished_at - self.started_at).total_seconds()
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_name": self.source.name if self.source else "",
            "status": self.status,
            "items_found": self.items_found,
            "items_new": self.items_new,
            "error_msg": self.error_msg,
            "duration_seconds": duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
