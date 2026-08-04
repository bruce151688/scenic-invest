"""
定时任务调度器 - 每日自动抓取
"""
import asyncio
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Source, CrawlLog, Product
from scrapers.registry import get_scraper_for_url


# 全局调度器实例
scheduler = AsyncIOScheduler()


def init_scheduler():
    """初始化并启动定时任务调度器"""
    # 每天早上 8:00 执行全量抓取
    scheduler.add_job(
        crawl_all_active_sources,
        CronTrigger(hour=8, minute=0),
        id="daily_crawl_all",
        name="每日全量抓取",
        replace_existing=True,
    )

    # 每6小时执行一次高频源抓取
    scheduler.add_job(
        crawl_high_frequency_sources,
        IntervalTrigger(hours=6),
        id="high_freq_crawl",
        name="高频源抓取",
        replace_existing=True,
    )

    scheduler.start()
    print("[定时任务] 调度器已启动")


async def crawl_all_active_sources():
    """抓取所有活跃的抓取源"""
    print(f"[定时任务] 开始每日全量抓取 {datetime.now()}")
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.is_active == True).all()
        for source in sources:
            await crawl_single_source(source.id, db)
    finally:
        db.close()
    print(f"[定时任务] 每日全量抓取完成 {datetime.now()}")


async def crawl_high_frequency_sources():
    """抓取高频源（频率 < 12小时）"""
    print(f"[定时任务] 开始高频抓取 {datetime.now()}")
    db = SessionLocal()
    try:
        sources = (
            db.query(Source)
            .filter(
                Source.is_active == True,
                Source.crawl_frequency_hours <= 12,
            )
            .all()
        )
        for source in sources:
            await crawl_single_source(source.id, db)
    finally:
        db.close()


async def crawl_single_source(source_id: int, db: Optional[Session] = None):
    """
    抓取单个数据源。
    如果 db 为 None，则创建自己的会话。
    """
    own_db = db is None
    if own_db:
        db = SessionLocal()

    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.is_active:
            return

        # 创建抓取日志
        crawl_log = CrawlLog(
            source_id=source.id,
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(crawl_log)
        db.commit()

        # 匹配爬虫
        ScraperClass = get_scraper_for_url(source.url)
        if ScraperClass is None:
            # 使用通用爬虫
            from scrapers.sites.example import GenericScraper
            ScraperClass = GenericScraper

        items_found = 0
        items_new = 0

        async with ScraperClass({"source_id": source.id}) as scraper:
            # 第一步：获取产品列表URL
            detail_urls = await scraper.fetch_list(source.url)

            # 第二步：逐个抓取详情
            for detail_url in detail_urls:
                items_found += 1

                # 去重检查
                existing = (
                    db.query(Product)
                    .filter(Product.source_url == detail_url)
                    .first()
                )
                if existing:
                    continue

                try:
                    product_data = await scraper.fetch_detail(detail_url)
                    if product_data and product_data.title:
                        # 保存产品
                        product = Product(
                            title=product_data.title,
                            description=product_data.description,
                            source_id=source.id,
                            source_url=product_data.source_url,
                            contact_info=product_data.to_dict().get("contact_info", {}),
                            location=product_data.to_dict().get("location", {}),
                            invest_range=product_data.invest_range,
                            price_range=product_data.price_range,
                            tags=product_data.tags,
                            status="pending_review",  # 爬取的产品默认待审核
                        )
                        db.add(product)
                        db.flush()  # 获取 product.id

                        # 下载图片
                        from utils import download_image
                        for idx, img_url in enumerate(product_data.image_urls[:20]):
                            result = await download_image(img_url, product_data.title)
                            if result:
                                from models import ProductImage
                                image = ProductImage(
                                    product_id=product.id,
                                    url=img_url,
                                    local_path=result["local_path"],
                                    thumbnail_path=result["thumbnail_path"],
                                    sort_order=idx,
                                    is_cover=(idx == 0),
                                )
                                db.add(image)

                        # 保存视频
                        from models import ProductVideo
                        from utils import detect_video_platform, get_bilibili_embed
                        for vid_url in product_data.video_urls:
                            platform = detect_video_platform(vid_url)
                            embed = ""
                            if platform == "bilibili":
                                embed = get_bilibili_embed(vid_url)
                            video = ProductVideo(
                                product_id=product.id,
                                url=vid_url,
                                platform=platform,
                                embed_code=embed,
                            )
                            db.add(video)

                        items_new += 1
                        db.commit()

                except Exception as e:
                    print(f"抓取详情失败 [{detail_url}]: {e}")
                    continue

                # 请求间隔
                await asyncio.sleep(2)

        # 更新抓取日志
        crawl_log.status = "success"
        crawl_log.items_found = items_found
        crawl_log.items_new = items_new
        crawl_log.finished_at = datetime.utcnow()

        # 更新源的最后抓取信息
        source.last_crawl_at = datetime.utcnow()
        source.last_crawl_status = "success"
        db.commit()

    except Exception as e:
        # 记录失败
        if "crawl_log" in locals():
            crawl_log.status = "failed"
            crawl_log.error_msg = str(e)[:2000]
            crawl_log.finished_at = datetime.utcnow()

        # 更新源状态
        source = db.query(Source).filter(Source.id == source_id).first()
        if source:
            source.last_crawl_at = datetime.utcnow()
            source.last_crawl_status = "failed"

        db.commit()
        print(f"抓取失败 [source_id={source_id}]: {e}")

    finally:
        if own_db and db:
            db.close()
