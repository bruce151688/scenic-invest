"""
产品管理 API 路由
"""
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from auth import get_current_user, require_editor, require_admin
from database import get_db
from models import (
    Product, ProductImage, ProductVideo,
    Category, Source, User,
)
from config import MAX_UPLOAD_SIZE, ALLOWED_IMAGE_TYPES, IMAGES_DIR

router = APIRouter(prefix="/api/products", tags=["产品"])


# ====== 请求/响应模型 ======

class ContactInfo(BaseModel):
    phone: str = ""
    wechat: str = ""
    email: str = ""
    website: str = ""


class LocationInfo(BaseModel):
    province: str = ""
    city: str = ""
    scenic_name: str = ""


class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str = ""
    category_id: int | None = None
    source_url: str = ""
    contact_info: ContactInfo = ContactInfo()
    location: LocationInfo = LocationInfo()
    invest_range: str = ""
    price_range: str = ""
    tags: list[str] = []


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category_id: int | None = None
    source_url: str | None = None
    contact_info: ContactInfo | None = None
    location: LocationInfo | None = None
    invest_range: str | None = None
    price_range: str | None = None
    tags: list[str] | None = None
    status: str | None = None  # active / pending_review / archived


# ====== 产品接口 ======

@router.get("", summary="产品列表（搜索+筛选+分页）")
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query("", description="关键词搜索（标题+描述）"),
    category_id: int | None = Query(None, description="分类ID筛选"),
    sub_category_id: int | None = Query(None, description="子分类ID筛选"),
    province: str = Query("", description="省份筛选"),
    city: str = Query("", description="城市筛选"),
    invest_range: str = Query("", description="投资区间"),
    status: str = Query("active", description="状态筛选"),
    sort_by: str = Query("newest", description="排序：newest / popular"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Product)

    # 状态过滤
    if status:
        query = query.filter(Product.status == status)

    # 关键词搜索
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            or_(
                Product.title.ilike(kw),
                Product.description.ilike(kw),
            )
        )

    # 分类筛选
    if category_id:
        # 包含子分类
        sub_ids = [category_id]
        children = db.query(Category).filter(Category.parent_id == category_id).all()
        sub_ids.extend([c.id for c in children])
        query = query.filter(Product.category_id.in_(sub_ids))
    elif sub_category_id:
        query = query.filter(Product.category_id == sub_category_id)

    # 地区筛选
    if province:
        query = query.filter(Product.location["province"].astext == province)
    if city:
        query = query.filter(Product.location["city"].astext.ilike(f"%{city}%"))

    # 投资区间筛选
    if invest_range:
        query = query.filter(Product.invest_range == invest_range)

    # 排序
    if sort_by == "popular":
        query = query.order_by(desc(Product.view_count), desc(Product.created_at))
    else:
        query = query.order_by(desc(Product.created_at))

    # 分页
    total = query.count()
    products = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [p.to_summary() for p in products],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{product_id}", summary="产品详情")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # 增加浏览计数
    product.view_count += 1
    db.commit()

    return product.to_dict()


@router.post("", summary="手动添加产品")
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    # 验证分类
    if data.category_id:
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="分类不存在")

    product = Product(
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        source_url=data.source_url,
        contact_info=data.contact_info.model_dump(),
        location=data.location.model_dump(),
        invest_range=data.invest_range,
        price_range=data.price_range,
        tags=data.tags,
        status="active",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product.to_dict()


@router.put("/{product_id}", summary="更新产品")
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("contact_info", "location") and value is not None:
            setattr(product, key, value if isinstance(value, dict) else value.model_dump())
        elif value is not None:
            setattr(product, key, value)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product.to_dict()


@router.delete("/{product_id}", summary="删除产品")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    db.delete(product)
    db.commit()
    return {"message": "删除成功"}


# ====== 图片上传接口 ======

@router.post("/{product_id}/images/upload", summary="上传产品图片")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    is_cover: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="不支持的图片格式")

    # 验证大小
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="图片超过10MB限制")

    # 保存文件
    import os
    from utils import make_image_path, url_hash
    import hashlib
    from PIL import Image as PILImage
    import io

    file_hash = hashlib.md5(content).hexdigest()
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{file_hash}.{ext}"
    filepath = make_image_path(filename)

    with open(filepath, "wb") as f:
        f.write(content)

    # 生成缩略图
    thumb_filename = f"{file_hash}_thumb.{ext}"
    thumb_path = make_image_path(thumb_filename)
    img = PILImage.open(io.BytesIO(content))
    img.thumbnail((400, 300), PILImage.LANCZOS)
    img.save(thumb_path, quality=85, optimize=True)

    relative_path = filepath.relative_to(IMAGES_DIR.parent).as_posix()
    relative_thumb = thumb_path.relative_to(IMAGES_DIR.parent).as_posix()

    # 如果是封面，先取消其他封面
    if is_cover:
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_cover == True,
        ).update({"is_cover": False})

    # 排序号
    max_order = db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    ).count()

    image = ProductImage(
        product_id=product_id,
        url="",
        local_path=relative_path,
        thumbnail_path=relative_thumb,
        alt_text=product.title,
        sort_order=max_order + 1,
        is_cover=is_cover or (max_order == 0),
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image.to_dict()


@router.delete("/images/{image_id}", summary="删除产品图片")
def delete_product_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")

    # 删除文件
    import os
    from config import BASE_DIR
    if image.local_path:
        filepath = BASE_DIR / image.local_path
        if filepath.exists():
            os.remove(filepath)
    if image.thumbnail_path:
        thumbpath = BASE_DIR / image.thumbnail_path
        if thumbpath.exists():
            os.remove(thumbpath)

    db.delete(image)
    db.commit()
    return {"message": "删除成功"}


# ====== 视频接口 ======

class VideoAdd(BaseModel):
    url: str = Field(..., min_length=1)
    platform: str = "other"
    embed_code: str = ""
    title: str = ""


@router.post("/{product_id}/videos", summary="添加产品视频")
def add_product_video(
    product_id: int,
    data: VideoAdd,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    video = ProductVideo(
        product_id=product_id,
        url=data.url,
        platform=data.platform,
        embed_code=data.embed_code,
        title=data.title,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video.to_dict()


@router.delete("/videos/{video_id}", summary="删除产品视频")
def delete_product_video(
    video_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    video = db.query(ProductVideo).filter(ProductVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    db.delete(video)
    db.commit()
    return {"message": "删除成功"}


# ====== 统计接口 ======

@router.get("/stats/summary", summary="获取产品统计")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Product).filter(Product.status == "active").count()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_new = db.query(Product).filter(
        Product.created_at >= today,
        Product.status == "active",
    ).count()

    # 各分类数量
    categories = db.query(Category).filter(Category.parent_id.is_(None)).all()
    cat_stats = []
    for cat in categories:
        children = db.query(Category).filter(Category.parent_id == cat.id).all()
        sub_ids = [cat.id] + [c.id for c in children]
        count = db.query(Product).filter(
            Product.category_id.in_(sub_ids),
            Product.status == "active",
        ).count()
        cat_stats.append({
            "category": cat.name,
            "icon": cat.icon,
            "count": count,
        })

    return {
        "total_products": total,
        "today_new": today_new,
        "by_category": cat_stats,
    }
