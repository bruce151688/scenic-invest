"""
景区二消产品搜罗平台 - FastAPI 入口
"""
import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 确保 backend 目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import HOST, PORT, DATA_DIR
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("=" * 50)
    print("  景区二消产品搜罗平台 启动中...")
    print("=" * 50)

    # 初始化数据库
    init_db()
    print("[数据库] 初始化完成")

    # 初始化分类数据
    _init_default_categories()

    # 启动定时任务
    from scheduler import init_scheduler
    init_scheduler()
    print(f"[服务] 运行在 http://{HOST}:{PORT}")
    print("[文档] API 文档: http://localhost:8000/docs")
    print("=" * 50)

    yield

    # 关闭时
    from scheduler import scheduler
    scheduler.shutdown()
    print("[服务] 已关闭")


app = FastAPI(
    title="景区二消产品搜罗平台",
    description="搜罗全国/全球景区内二消产品（吃住行游购娱），"
                "支持自动抓取、分类浏览、图片视频展示、商家联系方式查询",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件挂载（图片等）
app.mount("/static", StaticFiles(directory=str(DATA_DIR)), name="static")

# 注册路由
from routers.auth_router import router as auth_router
from routers.category_router import router as category_router
from routers.product_router import router as product_router
from routers.source_router import router as source_router

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(source_router)


@app.get("/api/health", tags=["系统"])
def health_check():
    """健康检查"""
    return {"status": "ok", "service": "景区二消产品搜罗平台"}


# ====== 生产模式：托管前端静态文件 ======
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="frontend_assets")
    app.mount("/icons", StaticFiles(directory=FRONTEND_DIR / "icons"), name="frontend_icons")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        """SPA fallback: 非API路径返回前端页面"""
        if full_path.startswith("api/") or full_path.startswith("static/"):
            raise HTTPException(404)
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        return {"message": "前端未构建"}

# ====== 默认分类初始化 ======

def _init_default_categories():
    """初始化默认产品分类体系"""
    from database import SessionLocal
    from models import Category

    db = SessionLocal()
    try:
        # 检查是否已有分类数据
        existing = db.query(Category).count()
        if existing > 0:
            return

        categories = [
            ("🎢", "互动游乐", [
                ("🎮", "科技互动", "VR/AR/MR体验、全息投影、互动投影"),
                ("🧗", "户外探险", "丛林穿越、攀岩、滑索、蹦极"),
                ("🏄", "水上项目", "漂流、皮划艇、水上乐园"),
                ("👨‍👩‍👧", "亲子游乐", "无动力乐园、儿童体验馆"),
                ("🎪", "沉浸式体验", "沉浸式剧场、密室逃脱、剧本杀"),
            ]),
            ("🍽️", "特色餐饮", [
                ("🏰", "主题餐厅", "景区特色主题餐厅"),
                ("🍢", "网红小吃", "网红打卡小吃"),
                ("🎁", "地方特产", "地方特产、伴手礼"),
                ("🚚", "移动餐车", "移动餐车、美食集市"),
            ]),
            ("🏨", "主题住宿", [
                ("⛺", "星空帐篷", "星空帐篷、泡泡屋"),
                ("🏡", "特色民宿", "树屋、水上屋、特色民宿"),
                ("🚐", "房车营地", "房车营地、自驾营地"),
            ]),
            ("🚡", "景区交通", [
                ("🚂", "观光车", "观光小火车、电瓶车"),
                ("🚠", "索道缆车", "索道、缆车、观光电梯"),
                ("🛴", "共享代步", "共享滑板车、平衡车"),
                ("⛵", "游船画舫", "游船、画舫、水上巴士"),
            ]),
            ("🛍️", "文创购物", [
                ("🧸", "IP衍生品", "景区IP衍生品、周边"),
                ("🎨", "文创伴手礼", "文创纪念品、伴手礼"),
                ("🧶", "非遗手作", "非遗体验、手工坊"),
                ("🤖", "智能零售", "无人零售、盲盒机"),
            ]),
            ("🎭", "演艺娱乐", [
                ("🏛️", "实景演出", "大型实景演出、舞台剧"),
                ("✨", "光影水秀", "光影秀、水幕秀、灯光节"),
                ("🎵", "街头演艺", "街头艺人、行为艺术"),
                ("🌙", "夜间经济", "夜游、夜市、酒吧街"),
            ]),
            ("📸", "网红打卡", [
                ("📷", "拍照装置", "艺术装置、拍照打卡点"),
                ("🏞️", "观景平台", "天空之境、玻璃栈道"),
                ("🌸", "季节性活动", "花海、灯会、冰雪节"),
            ]),
        ]

        for icon, name, children in categories:
            parent = Category(name=name, icon=icon, sort_order=len(db.query(Category).all()))
            db.add(parent)
            db.flush()

            for child_icon, child_name, child_desc in children:
                child = Category(
                    name=child_name,
                    icon=child_icon,
                    parent_id=parent.id,
                    description=child_desc,
                    sort_order=len(children),
                )
                db.add(child)

        db.commit()
        print("[数据库] 默认分类数据已初始化")

    finally:
        db.close()


# ====== 直接运行 ======
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
