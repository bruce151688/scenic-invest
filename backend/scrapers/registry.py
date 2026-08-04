"""
爬虫注册表 - 根据URL自动匹配对应爬虫
"""
from typing import Dict, Type, Optional
from urllib.parse import urlparse

from scrapers.base import BaseScraper

# 爬虫注册表: {域名关键字: 爬虫类}
_scraper_registry: Dict[str, Type[BaseScraper]] = {}


def register_scraper(domain_pattern: str):
    """装饰器：注册爬虫到注册表

    Usage:
        @register_scraper("example.com")
        class ExampleScraper(BaseScraper):
            ...
    """

    def decorator(cls: Type[BaseScraper]):
        _scraper_registry[domain_pattern] = cls
        return cls

    return decorator


def get_scraper_for_url(url: str) -> Optional[Type[BaseScraper]]:
    """根据URL找到匹配的爬虫类"""
    domain = urlparse(url).netloc.lower()
    for pattern, scraper_cls in _scraper_registry.items():
        if pattern in domain:
            return scraper_cls
    return None


def get_all_scrapers() -> Dict[str, Type[BaseScraper]]:
    return dict(_scraper_registry)


# ========== 导入所有爬虫实现（确保被注册） ==========
import scrapers.sites.example  # noqa: E402, F401
import scrapers.sites.chinese_platforms  # noqa: E402, F401
