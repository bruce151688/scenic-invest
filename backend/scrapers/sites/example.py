"""
示例爬虫 - 通用HTML网站爬虫模板

这是一个通用爬虫，适合大多数展示产品列表的网站。
用户可以基于此模板快速适配自己的目标网站。
"""
import re
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, ScrapedProduct
from scrapers.registry import register_scraper


# ============================================================
# 示例1: 通用爬虫 - 自动检测页面中的产品信息
# ============================================================
class GenericScraper(BaseScraper):
    """
    通用爬虫 - 尝试自动检测页面结构来提取产品信息。
    适用场景：没有时间编写专用爬虫时的快速方案。
    """

    site_name = "通用抓取器"

    async def fetch_list(self, url: str) -> List[str]:
        soup = await self.fetch_page(url)
        if not soup:
            return []

        links = set()
        # 查找所有可能是产品详情页的链接
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(url, href)
            text = a_tag.get_text(strip=True)

            # 过滤：链接文字较长且URL看起来像详情页
            if len(text) > 4 and self._looks_like_detail_url(full_url, url):
                links.add(full_url)

        return list(links)[:50]  # 限制50个

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        # 提取标题
        title = self._extract_title(soup)

        # 提取描述
        description = self._extract_description(soup)

        # 提取图片
        images = self._extract_images(soup, url)

        # 提取视频
        videos = self._extract_videos(soup, url)

        # 提取联系方式
        full_text = soup.get_text()
        phone = self.extract_phone(full_text)
        wechat = self.extract_wechat(full_text)
        email = self.extract_email(full_text)

        return ScrapedProduct(
            title=title or "未知产品",
            description=description[:2000] if description else "",
            source_url=url,
            image_urls=images,
            video_urls=videos,
            contact_phone=phone,
            contact_wechat=wechat,
            contact_email=email,
            tags=self._extract_keywords(title, full_text),
        )

    def _looks_like_detail_url(self, url: str, base_url: str) -> bool:
        """判断URL是否像产品详情页"""
        patterns = [
            r'/detail', r'/product', r'/goods', r'/item', r'/article',
            r'/show', r'/info', r'/content', r'/view', r'/news',
            r'\d{4,}', r'id=', r'pid=', r'cid=',
        ]
        low_url = url.lower()
        return any(re.search(p, low_url) for p in patterns)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        # 优先 meta og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        # 然后 h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        # 最后是页面 title
        if soup.title:
            return soup.title.get_text(strip=True)
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        # 优先 meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        # 取正文前几段
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 20:
                paragraphs.append(text)
            if len(paragraphs) >= 5:
                break
        return "\n".join(paragraphs)

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        images = []
        # 在主要内容区域找图片
        main = soup.find("article") or soup.find("main") or soup
        for img in main.find_all("img", src=True):
            src = img["src"]
            full_url = urljoin(base_url, src)
            # 过滤小图标和logo
            if not self._is_small_icon(full_url):
                images.append(full_url)
        return list(dict.fromkeys(images))[:20]  # 去重+限制

    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        videos = []
        # iframe 视频
        for iframe in soup.find_all("iframe", src=True):
            src = iframe["src"]
            if any(p in src.lower() for p in ["player", "video", "bilibili", "youtube"]):
                videos.append(urljoin(base_url, src))
        # video 标签
        for v in soup.find_all("video"):
            source = v.find("source")
            if source and source.get("src"):
                videos.append(urljoin(base_url, source["src"]))
        return list(set(videos))

    def _is_small_icon(self, url: str) -> bool:
        return any(kw in url.lower() for kw in ["icon", "logo", "avatar", "qrcode", "banner"])

    def _extract_keywords(self, title: str, text: str) -> List[str]:
        """从文本中提取景区/产品相关关键词"""
        keyword_list = [
            "景区", "游乐", "VR", "AR", "沉浸", "互动", "光影",
            "漂流", "攀岩", "索道", "观光", "露营", "帐篷", "民宿",
            "文创", "演艺", "实景", "水秀", "灯光", "打卡",
        ]
        combined = (title or "") + " " + (text or "")[:2000]
        found = [kw for kw in keyword_list if kw in combined]
        return found[:10]


# ============================================================
# 示例2: 专用爬虫模板 - 针对具体网站定制的爬虫
# ============================================================
@register_scraper("example-scenic-products.com")
class ExampleSiteScraper(BaseScraper):
    """
    专用爬虫模板

    替换 example-scenic-products.com 为实际目标网站域名。
    根据目标网站的HTML结构调整以下选择器。
    """

    site_name = "示例景区产品网"

    # ====== 配置项（按实际网站修改） ======
    LIST_ITEM_SELECTOR = "div.product-item a"  # 列表页产品链接的选择器
    TITLE_SELECTOR = "h1.product-title"  # 详情页标题选择器
    DESC_SELECTOR = "div.product-desc"  # 详情页描述选择器
    IMAGE_SELECTOR = "div.product-gallery img"  # 图片选择器
    VIDEO_SELECTOR = "div.product-video iframe, video source"  # 视频选择器
    NEXT_PAGE_SELECTOR = "a.next-page"  # 下一页选择器
    CONTACT_SELECTOR = "div.contact-info"  # 联系方式选择器

    async def fetch_list(self, url: str) -> List[str]:
        """抓取列表页，返回详情页URL列表"""
        links = []
        page_url = url

        # 抓取前3页
        for _ in range(3):
            soup = await self.fetch_page(page_url)
            if not soup:
                break

            for a_tag in soup.select(self.LIST_ITEM_SELECTOR):
                href = a_tag.get("href", "")
                if href:
                    full_url = urljoin(page_url, href)
                    links.append(full_url)

            # 下一页
            next_btn = soup.select_one(self.NEXT_PAGE_SELECTOR)
            if next_btn and next_btn.get("href"):
                page_url = urljoin(page_url, next_btn["href"])
            else:
                break

        return list(dict.fromkeys(links))  # 去重

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        """抓取产品详情页"""
        soup = await self.fetch_page(url)
        if not soup:
            return None

        # 标题
        title_el = soup.select_one(self.TITLE_SELECTOR)
        title = title_el.get_text(strip=True) if title_el else ""

        # 描述
        desc_el = soup.select_one(self.DESC_SELECTOR)
        description = desc_el.get_text(strip=True) if desc_el else ""

        # 图片
        images = []
        for img in soup.select(self.IMAGE_SELECTOR):
            src = img.get("src") or img.get("data-src")
            if src:
                images.append(urljoin(url, src))

        # 视频
        videos = []
        for vid_el in soup.select(self.VIDEO_SELECTOR):
            vid_src = vid_el.get("src") or vid_el.get("href")
            if vid_src:
                videos.append(urljoin(url, vid_src))

        # 联系方式
        contact_text = ""
        contact_el = soup.select_one(self.CONTACT_SELECTOR)
        if contact_el:
            contact_text = contact_el.get_text()
        full_text = soup.get_text()

        return ScrapedProduct(
            title=title or "未知产品",
            description=description[:3000],
            source_url=url,
            image_urls=images[:20],
            video_urls=videos[:5],
            contact_phone=self.extract_phone(contact_text or full_text),
            contact_wechat=self.extract_wechat(contact_text or full_text),
            contact_email=self.extract_email(contact_text or full_text),
        )


# ============================================================
# 示例3: RSS 源抓取器
# ============================================================
class RSSScraper(BaseScraper):
    """RSS 源抓取器 - 适合有RSS订阅的行业网站"""

    site_name = "RSS抓取器"

    async def fetch_list(self, url: str) -> List[str]:
        soup = await self.fetch_page(url)
        if not soup:
            return []

        links = []
        # RSS item link
        for item in soup.find_all("item"):
            link = item.find("link")
            if link:
                links.append(link.get_text(strip=True))

        # Atom entry link
        for entry in soup.find_all("entry"):
            link = entry.find("link")
            if link:
                href = link.get("href", "")
                if href:
                    links.append(href)

        return links[:100]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc else ""

        images = []
        for img in soup.find_all("img", src=True):
            src = urljoin(url, img["src"])
            if not any(k in src.lower() for k in ["icon", "logo", "avatar"]):
                images.append(src)

        return ScrapedProduct(
            title=title or "未命名",
            description=description[:2000],
            source_url=url,
            image_urls=images[:15],
        )
