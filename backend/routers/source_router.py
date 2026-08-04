"""
抓取源管理 API + 手动触发抓取
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user, require_admin, require_editor
from database import get_db
from models import Source, CrawlLog, User
from scheduler import crawl_single_source

router = APIRouter(prefix="/api/sources", tags=["抓取源"])


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    url: str = Field(..., min_length=1, max_length=512)
    scraper_type: str = "html"
    crawl_frequency_hours: int = 24
    is_active: bool = True
    notes: str = ""


class SourceUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    scraper_type: str | None = None
    crawl_frequency_hours: int | None = None
    is_active: bool | None = None
    notes: str | None = None


@router.get("", summary="抓取源列表")
def list_sources(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sources = db.query(Source).order_by(Source.created_at.desc()).all()
    return {"items": [s.to_dict() for s in sources], "total": len(sources)}


@router.get("/{source_id}", summary="抓取源详情")
def get_source(
    source_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="抓取源不存在")

    # 附带最近的抓取日志
    recent_logs = (
        db.query(CrawlLog)
        .filter(CrawlLog.source_id == source_id)
        .order_by(CrawlLog.started_at.desc())
        .limit(10)
        .all()
    )
    data = source.to_dict()
    data["recent_logs"] = [log.to_dict() for log in recent_logs]
    return data


@router.post("", summary="添加抓取源")
def create_source(
    data: SourceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    source = Source(
        name=data.name,
        url=data.url,
        scraper_type=data.scraper_type,
        crawl_frequency_hours=data.crawl_frequency_hours,
        is_active=data.is_active,
        notes=data.notes,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source.to_dict()


@router.put("/{source_id}", summary="更新抓取源")
def update_source(
    source_id: int,
    data: SourceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="抓取源不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source.to_dict()


@router.delete("/{source_id}", summary="删除抓取源")
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="抓取源不存在")
    db.delete(source)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{source_id}/crawl", summary="手动触发单源抓取")
async def trigger_crawl(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_editor),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="抓取源不存在")

    # 后台执行抓取
    background_tasks.add_task(crawl_single_source, source_id)
    return {"message": f"已触发抓取: {source.name}", "source_id": source_id}


@router.post("/crawl-all", summary="手动触发全部抓取")
async def trigger_crawl_all(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    active_sources = db.query(Source).filter(Source.is_active == True).all()
    for source in active_sources:
        background_tasks.add_task(crawl_single_source, source.id)
    return {
        "message": f"已触发 {len(active_sources)} 个源的抓取",
        "source_count": len(active_sources),
    }


@router.get("/{source_id}/logs", summary="查看抓取日志")
def list_crawl_logs(
    source_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logs_query = (
        db.query(CrawlLog)
        .filter(CrawlLog.source_id == source_id)
        .order_by(CrawlLog.started_at.desc())
    )
    total = logs_query.count()
    logs = logs_query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [log.to_dict() for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
