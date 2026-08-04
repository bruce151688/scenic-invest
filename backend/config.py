"""
景区二消产品搜罗平台 - 配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据目录（本地用 data/，生产环境用 Render 持久磁盘）
if os.getenv("RENDER") or os.path.isdir("/var/data"):
    DATA_DIR = Path("/var/data")
else:
    DATA_DIR = BASE_DIR / "data"

IMAGES_DIR = DATA_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 数据库
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'scenic_invest.db'}")

# JWT 认证配置
SECRET_KEY = os.getenv("SECRET_KEY", "scenic-invest-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 爬虫配置
CRAWLER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
CRAWLER_REQUEST_DELAY = 2  # 请求间隔（秒）
CRAWLER_DEFAULT_FREQUENCY_HOURS = 24  # 默认抓取频率（小时）
CRAWLER_MAX_IMAGES_PER_PRODUCT = 10  # 每个产品最多下载图片数

# 分页
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 服务器
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 上传文件
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]

# 缩略图
THUMBNAIL_SIZE = (400, 300)
