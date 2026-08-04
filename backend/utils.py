"""
工具函数：图片下载、缩略图生成、通用辅助
"""
import hashlib
import os
from pathlib import Path
from typing import Optional

import httpx
from PIL import Image

from config import IMAGES_DIR, THUMBNAIL_SIZE, CRAWLER_USER_AGENT


def url_hash(url: str) -> str:
    """URL 哈希（用于去重和文件名）"""
    return hashlib.md5(url.encode()).hexdigest()


def make_image_path(filename: str) -> Path:
    """生成图片存储路径，按日期分子目录"""
    import datetime
    date_dir = datetime.date.today().strftime("%Y/%m/%d")
    full_dir = IMAGES_DIR / date_dir
    full_dir.mkdir(parents=True, exist_ok=True)
    return full_dir / filename


async def download_image(url: str, product_title: str = "") -> Optional[dict]:
    """
    下载单张图片并生成缩略图。
    返回 {"local_path": ..., "thumbnail_path": ...} 或 None
    """
    if not url:
        return None

    headers = {"User-Agent": CRAWLER_USER_AGENT}
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None

            content_type = resp.headers.get("content-type", "")
            ext = _get_ext(content_type)
            if not ext:
                return None

            # 生成唯一文件名
            filename = f"{url_hash(url)}.{ext}"
            filepath = make_image_path(filename)
            thumb_filename = f"{url_hash(url)}_thumb.{ext}"
            thumb_path = make_image_path(thumb_filename)

            # 保存原图
            with open(filepath, "wb") as f:
                f.write(resp.content)

            # 生成缩略图
            img = Image.open(filepath)
            img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
            img.save(thumb_path, quality=85, optimize=True)

            # 返回相对路径
            relative_dir = filepath.relative_to(IMAGES_DIR.parent).as_posix()
            relative_thumb = thumb_path.relative_to(IMAGES_DIR.parent).as_posix()

            return {
                "local_path": relative_dir,
                "thumbnail_path": relative_thumb,
                "original_url": url,
            }
    except Exception as e:
        print(f"下载图片失败 [{url}]: {e}")
        return None


def _get_ext(content_type: str) -> str:
    """根据 Content-Type 获取文件扩展名"""
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
        "image/bmp": "bmp",
        "image/svg+xml": "svg",
    }
    return mapping.get(content_type.split(";")[0].strip(), "")


def detect_video_platform(url: str) -> str:
    """检测视频链接的平台"""
    url_lower = url.lower()
    if "bilibili.com" in url_lower or "b23.tv" in url_lower:
        return "bilibili"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "douyin.com" in url_lower or "v.douyin.com" in url_lower:
        return "douyin"
    elif "kuaishou.com" in url_lower:
        return "kuaishou"
    return "other"


def get_bilibili_embed(url: str) -> str:
    """生成B站视频嵌入代码"""
    import re
    # 提取BV号或aid
    bv_match = re.search(r'(BV[a-zA-Z0-9]+)', url)
    if bv_match:
        bvid = bv_match.group(1)
        return f'<iframe src="//player.bilibili.com/player.html?bvid={bvid}&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>'
    return ""
