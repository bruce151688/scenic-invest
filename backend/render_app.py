"""
Render 生产应用 - 精简健壮版
"""
import sys, os, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print("[STARTUP] Importing fastapi...", flush=True)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

print("[STARTUP] Creating app...", flush=True)
app = FastAPI(title="景区二消产品搜罗平台", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "景区二消产品搜罗平台"}

@app.exception_handler(Exception)
async def global_handler(request, exc):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# ====== 注册路由 ======
print("[STARTUP] Importing database...", flush=True)
try:
    from database import init_db, SessionLocal
    from models import Category, Product
    init_db()
    print("[STARTUP] DB ready", flush=True)
except Exception as e:
    print(f"[STARTUP] DB warning (non-fatal): {e}", flush=True)

print("[STARTUP] Importing routers...", flush=True)
from routers.auth_router import router as auth_router
from routers.category_router import router as category_router
from routers.product_router import router as product_router
from routers.source_router import router as source_router

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(source_router)


# ====== 辅助函数（必须在调用前定义） ======

def _init_categories(db):
    data = [
        ("🎢", "互动游乐", [("🎮", "科技互动", ""), ("🧗", "户外探险", ""), ("🏄", "水上项目", ""), ("👨‍👩‍👧", "亲子游乐", ""), ("🎪", "沉浸式体验", "")]),
        ("🍽️", "特色餐饮", [("🏰", "主题餐厅", ""), ("🍢", "网红小吃", ""), ("🎁", "地方特产", ""), ("🚚", "移动餐车", "")]),
        ("🏨", "主题住宿", [("⛺", "星空帐篷", ""), ("🏡", "特色民宿", ""), ("🚐", "房车营地", "")]),
        ("🚡", "景区交通", [("🚂", "观光车", ""), ("🚠", "索道缆车", ""), ("🛴", "共享代步", ""), ("⛵", "游船画舫", "")]),
        ("🛍️", "文创购物", [("🧸", "IP衍生品", ""), ("🎨", "文创伴手礼", ""), ("🧶", "非遗手作", ""), ("🤖", "智能零售", "")]),
        ("🎭", "演艺娱乐", [("🏛️", "实景演出", ""), ("✨", "光影水秀", ""), ("🎵", "街头演艺", ""), ("🌙", "夜间经济", "")]),
        ("📸", "网红打卡", [("📷", "拍照装置", ""), ("🏞️", "观景平台", ""), ("🌸", "季节性活动", "")]),
    ]
    for icon, name, children in data:
        parent = Category(name=name, icon=icon)
        db.add(parent)
        db.flush()
        for ci, cn, cd in children:
            db.add(Category(name=cn, icon=ci, parent_id=parent.id, description=cd))
    db.commit()


def _init_sample_products(db):
    products = [
        Product(title="悬崖网红秋千", description="建在悬崖边的网红秋千。投资15-50万，回本3-6个月，年利润50-150万。", category_id=2, invest_range="15-50万", price_range="30-60元/人", contact_info={"phone":"13888880001","wechat":"cliff_swing888"}, location={"province":"浙江","city":"温州","scenic_name":"雁荡山"}, tags=["悬崖秋千","网红打卡","回本快"], status="active"),
        Product(title="沉浸式光影互动体验馆", description="全息投影+动作捕捉。投资50-200万，年利润200-500万。", category_id=1, invest_range="50-200万", price_range="50-120元/人", contact_info={"phone":"13999990002","wechat":"immersive_light"}, tags=["全息投影","沉浸式"], status="active"),
        Product(title="彩虹滑道", description="色彩鲜艳的多人滑道。投资20-80万，回本3-8个月。", category_id=4, invest_range="20-80万", price_range="20-50元/人", contact_info={"phone":"13777770003"}, tags=["彩虹滑道","亲子"], status="active"),
    ]
    for p in products:
        db.add(p)
    db.commit()


# ====== 种子数据初始化 ======
print("[STARTUP] Checking seed data...", flush=True)
try:
    db = SessionLocal()
    if db.query(Category).count() == 0:
        _init_categories(db)
    if db.query(Product).count() == 0:
        _init_sample_products(db)
    db.close()
    print("[STARTUP] Seed data ready", flush=True)
except Exception as e:
    print(f"[STARTUP] Seed warning: {e}", flush=True)

print("[STARTUP] ====== READY ======", flush=True)
