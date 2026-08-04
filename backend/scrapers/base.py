"""
爬虫基类 - 定义统一的抓取接口
"""
import hashlib
import re
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from config import CRAWLER_USER_AGENT, CRAWLER_REQUEST_DELAY
from utils import detect_video_platform, get_bilibili_embed


@dataclass
class ScrapedProduct:
    """爬虫抓取到的产品数据结构"""
    title: str
    description: str = ""
    source_url: str = ""
    # 图片URL列表
    image_urls: List[str] = field(default_factory=list)
    # 视频URL列表
    video_urls: List[str] = field(default_factory=list)
    # 联系方式
    contact_phone: str = ""
    contact_wechat: str = ""
    contact_email: str = ""
    contact_website: str = ""
    # 位置
    province: str = ""
    city: str = ""
    scenic_name: str = ""
    # 投资信息
    invest_range: str = ""
    price_range: str = ""
    # 标签
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "source_url": self.source_url,
            "image_urls": self.image_urls,
            "video_urls": self.video_urls,
            "contact_info": {
                "phone": self.contact_phone,
                "wechat": self.contact_wechat,
                "email": self.contact_email,
                "website": self.contact_website,
            },
            "location": {
                "province": self.province,
                "city": self.city,
                "scenic_name": self.scenic_name,
            },
            "invest_range": self.invest_range,
            "price_range": self.price_range,
            "tags": self.tags,
        }

    @property
    def url_hash(self) -> str:
        return hashlib.md5(self.source_url.encode()).hexdigest()


class BaseScraper(ABC):
    """爬虫基类"""

    # 子类需定义
    site_name: str = ""  # 网站名称

    def __init__(self, source_config: dict = None):
        self.config = source_config or {}
        self.headers = {
            "User-Agent": CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    @abstractmethod
    async def fetch_list(self, url: str) -> List[str]:
        """
        从列表页抓取产品详情页URL列表
        返回: 详情页URL列表
        """
        pass

    @abstractmethod
    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        """
        从详情页抓取产品详细信息
        返回: ScrapedProduct 或 None
        """
        pass

    async def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """获取页面并解析为 BeautifulSoup"""
        try:
            resp = await self.client.get(url)
            resp.encoding = resp.encoding or "utf-8"
            return BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            print(f"[{self.site_name}] 请求失败 {url}: {e}")
            return None

    async def fetch_json(self, url: str) -> Optional[dict]:
        """获取 JSON API 数据"""
        try:
            resp = await self.client.get(url)
            return resp.json()
        except Exception as e:
            print(f"[{self.site_name}] JSON请求失败 {url}: {e}")
            return None

    def extract_phone(self, text: str) -> str:
        """从文本中提取手机/电话号"""
        patterns = [
            r'1[3-9]\d{9}',  # 手机号
            r'0\d{2,3}-\d{7,8}',  # 座机
            r'400[-\s]?\d{3}[-\s]?\d{4}',  # 400电话
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                return match.group()
        return ""

    def extract_email(self, text: str) -> str:
        """从文本中提取邮箱"""
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group() if match else ""

    def extract_wechat(self, text: str) -> str:
        """从文本中提取微信号"""
        patterns = [
            r'微信[：:\s]*([a-zA-Z][a-zA-Z0-9_-]{5,19})',
            r'wechat[：:\s]*([a-zA-Z][a-zA-Z0-9_-]{5,19})',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
