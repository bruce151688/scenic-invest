"""
产品分类 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user, require_admin, require_editor
from database import get_db
from models import Category, User

router = APIRouter(prefix="/api/categories", tags=["分类"])


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    icon: str = Field(default="📦", max_length=8)
    parent_id: int | None = None
    sort_order: int = 0
    description: str = ""


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    parent_id: int | None = None
    sort_order: int | None = None
    description: str | None = None


@router.get("", summary="获取分类树")
def list_categories(db: Session = Depends(get_db)):
    # 获取根分类
    roots = (
        db.query(Category)
        .filter(Category.parent_id.is_(None))
        .order_by(Category.sort_order, Category.id)
        .all()
    )
    return {
        "items": [cat.to_dict() for cat in roots],
        "total": len(roots),
    }


@router.get("/all", summary="获取平级分类列表")
def list_all_categories(db: Session = Depends(get_db)):
    """获取所有分类（扁平列表，适合下拉选择）"""
    categories = db.query(Category).order_by(Category.sort_order, Category.id).all()

    def build_flat(cats, level=0, result=None):
        if result is None:
            result = []
        for cat in cats:
            result.append({
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "parent_id": cat.parent_id,
                "level": level,
            })
            if cat.children:
                build_flat(cat.children, level + 1, result)
        return result

    return {"items": build_flat(categories)}


@router.post("", summary="创建分类")
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    # 验证父分类存在
    if data.parent_id:
        parent = db.query(Category).filter(Category.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")

    cat = Category(
        name=data.name,
        icon=data.icon,
        parent_id=data.parent_id,
        sort_order=data.sort_order,
        description=data.description,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat.to_dict()


@router.put("/{category_id}", summary="更新分类")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    if data.name is not None:
        cat.name = data.name
    if data.icon is not None:
        cat.icon = data.icon
    if data.parent_id is not None:
        cat.parent_id = data.parent_id
    if data.sort_order is not None:
        cat.sort_order = data.sort_order
    if data.description is not None:
        cat.description = data.description
    db.commit()
    db.refresh(cat)
    return cat.to_dict()


@router.delete("/{category_id}", summary="删除分类")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 检查是否有子分类
    children = db.query(Category).filter(Category.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="请先删除子分类")
    # 检查是否有产品
    if cat.products.count() > 0:
        raise HTTPException(status_code=400, detail="该分类下还有产品，无法删除")
    db.delete(cat)
    db.commit()
    return {"message": "删除成功"}
