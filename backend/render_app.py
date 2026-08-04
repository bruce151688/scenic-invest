"""
Render 专用入口 - 生产模式 FastAPI 应用
"""
import sys
import os
from pathlib import Path

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import DATA_DIR, BASE_DIR
from database import init_db, SessionLocal
from models import Category

# 创建应用
app = FastAPI(
    title="景区二消产品搜罗平台",
    description="搜罗全国/全球景区内二消产品",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
from routers.auth_router import router as auth_router
from routers.category_router import router as category_router
from routers.product_router import router as product_router
from routers.source_router import router as source_router

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(source_router)


@app.on_event("startup")
def startup():
    """启动时初始化数据库和数据"""
    print("[Render] Initializing database...")
    init_db()

    # 初始化分类数据
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing == 0:
            categories_data = [
                ("🎢", "互动游乐", [
                    ("🎮", "科技互动", "VR/AR/MR体验、全息投影、互动投影"),
                    ("🧗", "户外探险", "丛林穿越、攀岩、滑索、蹦极"),
                    ("🏄", "水上项目", "漂流、皮划艇、水上乐园"),
                    ("👨‍👩‍👧", "亲子游乐", "无动力乐园、儿童体验馆"),
                    ("🎪", "沉浸式体验", "沉浸式剧场、密室逃脱、剧本杀"),
                ]),
                ("🍽️", "特色餐饮", [
                    ("🏰", "主题餐厅", ""), ("🍢", "网红小吃", ""),
                    ("🎁", "地方特产", ""), ("🚚", "移动餐车", ""),
                ]),
                ("🏨", "主题住宿", [
                    ("⛺", "星空帐篷", ""), ("🏡", "特色民宿", ""), ("🚐", "房车营地", ""),
                ]),
                ("🚡", "景区交通", [
                    ("🚂", "观光车", ""), ("🚠", "索道缆车", ""),
                    ("🛴", "共享代步", ""), ("⛵", "游船画舫", ""),
                ]),
                ("🛍️", "文创购物", [
                    ("🧸", "IP衍生品", ""), ("🎨", "文创伴手礼", ""),
                    ("🧶", "非遗手作", ""), ("🤖", "智能零售", ""),
                ]),
                ("🎭", "演艺娱乐", [
                    ("🏛️", "实景演出", ""), ("✨", "光影水秀", ""),
                    ("🎵", "街头演艺", ""), ("🌙", "夜间经济", ""),
                ]),
                ("📸", "网红打卡", [
                    ("📷", "拍照装置", ""), ("🏞️", "观景平台", ""), ("🌸", "季节性活动", ""),
                ]),
            ]
            for icon, name, children in categories_data:
                parent = Category(name=name, icon=icon, sort_order=len(db.query(Category).all()))
                db.add(parent)
                db.flush()
                for child_icon, child_name, child_desc in children:
                    db.add(Category(name=child_name, icon=child_icon, parent_id=parent.id, description=child_desc))
            db.commit()
            print("[Render] Categories initialized")
    finally:
        db.close()

    # 导入示例产品数据
    try:
        from models import Product
        db2 = SessionLocal()
        try:
            if db2.query(Product).count() == 0:
                products = [
                    Product(title="悬崖网红秋千 - 景区高空体验项目",
                            description="建在悬崖边的网红秋千，将游客荡出悬崖边缘，极致刺激体验。投资15-50万，回本周期3-6个月。",
                            category_id=2, invest_range="15-50万", price_range="30-60元/人",
                            contact_info={"phone":"13888880001","wechat":"cliff_swing888"},
                            location={"province":"浙江","city":"温州","scenic_name":"雁荡山"},
                            tags=["悬崖秋千","网红打卡","回本快"], status="active"),
                    Product(title="沉浸式光影互动体验馆",
                            description="全息投影+动作捕捉+互动感应，打造沉浸式光影空间。投资50-200万，年利润200-500万。",
                            category_id=1, invest_range="50-200万", price_range="50-120元/人",
                            contact_info={"phone":"13999990002","wechat":"immersive_light"},
                            location={"province":"广东","city":"深圳"},
                            tags=["全息投影","沉浸式","科技互动"], status="active"),
                    Product(title="彩虹滑道 - 亲子网红游乐设施",
                            description="色彩鲜艳的多人滑道，适合亲子家庭和年轻人。投资20-80万，回本3-8个月。",
                            category_id=4, invest_range="20-80万", price_range="20-50元/人",
                            contact_info={"phone":"13777770003"},
                            location={"province":"河南","city":"郑州"},
                            tags=["彩虹滑道","亲子","网红"], status="active"),
                ]
                for p in products:
                    db2.add(p)
                db2.commit()
                print(f"[Render] {len(products)} sample products created")
        finally:
            db2.close()
    except Exception as e:
        print(f"[Render] Sample data warning: {e}")

    print("[Render] Startup complete!")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "景区二消产品搜罗平台"}


# 前端静态文件（如果存在）
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    app.mount("/icons", StaticFiles(directory=FRONTEND_DIR / "icons"), name="icons")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404)
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        index = FRONTEND_DIR / "index.html"
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(404)
