"""
中国主流平台爬虫模块
支持：小红书、抖音、淘宝、今日头条、B站、微信公众号文章等
"""
import re
import json
from typing import List, Optional
from urllib.parse import urljoin, quote

from scrapers.base import BaseScraper, ScrapedProduct
from scrapers.registry import register_scraper


# ============================================================
# B站 (Bilibili) 爬虫 - 搜索景区/游乐项目相关视频
# ============================================================
@register_scraper("bilibili.com")
@register_scraper("b23.tv")
class BilibiliScraper(BaseScraper):
    """B站视频搜索爬虫 - 搜索景区二消项目评测/介绍视频"""

    site_name = "哔哩哔哩"

    async def fetch_list(self, url: str) -> List[str]:
        """
        B站搜索API
        URL格式: https://search.bilibili.com/all?keyword=景区游乐项目
        或直接搜索URL
        """
        # 使用 B站搜索API
        keyword = self._extract_keyword(url) or "景区 游乐项目 投资"
        search_url = (
            f"https://api.bilibili.com/x/web-interface/search/all/v2"
            f"?keyword={quote(keyword)}&page=1&page_size=30"
        )
        data = await self.fetch_json(search_url)
        if not data or data.get("code") != 0:
            return []

        links = []
        results = data.get("data", {}).get("result", [])
        for item in results:
            item_type = item.get("result_type", "")
            items = item.get("data", [])
            for sub in items[:20]:
                bvid = sub.get("bvid", "")
                if bvid:
                    links.append(f"https://www.bilibili.com/video/{bvid}")
                elif sub.get("arcurl"):
                    links.append(sub["arcurl"])

        return links[:30]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        # 提取视频信息
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")

        # B站视频封面图
        og_image = soup.find("meta", property="og:image")
        images = []
        if og_image:
            images.append(og_image.get("content", ""))

        # 提取标签
        tags = []
        tag_elements = soup.find_all("li", class_="tag")
        for tag_el in tag_elements:
            tag_text = tag_el.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)

        # 提取UP主信息作为联系方式参考
        full_text = soup.get_text()
        phone = self.extract_phone(full_text)
        wechat = self.extract_wechat(full_text)

        return ScrapedProduct(
            title=title or "B站视频",
            description=description[:2000],
            source_url=url,
            image_urls=images,
            video_urls=[url],
            contact_phone=phone,
            contact_wechat=wechat,
            tags=tags + self._extract_keywords(title, full_text),
        )

    def _extract_keyword(self, url: str) -> str:
        match = re.search(r'keyword=([^&]+)', url)
        if match:
            return match.group(1)
        return ""


# ============================================================
# 今日头条 爬虫
# ============================================================
@register_scraper("toutiao.com")
class ToutiaoScraper(BaseScraper):
    """今日头条搜索爬虫 - 搜索景区投资项目资讯"""

    site_name = "今日头条"

    async def fetch_list(self, url: str) -> List[str]:
        keyword = "景区 游乐项目 投资"
        search_url = (
            f"https://so.toutiao.com/search?"
            f"dvpf=pc&source=input&keyword={quote(keyword)}&page_num=0"
        )
        soup = await self.fetch_page(search_url)
        if not soup:
            return []

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/group/" in href or "/article/" in href or "/a" in href:
                full = urljoin("https://www.toutiao.com", href)
                links.append(full)
        return list(set(links))[:30]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

        description = ""
        article = soup.find("article")
        if article:
            description = article.get_text(strip=True)

        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if "http" in src and not any(k in src.lower() for k in ["icon", "logo", "avatar"]):
                images.append(urljoin(url, src))

        full_text = soup.get_text()
        tags = self._extract_keywords(title, full_text)

        return ScrapedProduct(
            title=title or "头条文章",
            description=description[:2000],
            source_url=url,
            image_urls=images[:10],
            tags=tags,
            contact_phone=self.extract_phone(full_text),
            contact_wechat=self.extract_wechat(full_text),
        )


# ============================================================
# 微信公众号文章搜索 (通过搜狗微信搜索)
# ============================================================
@register_scraper("weixin.sogou.com")
@register_scraper("mp.weixin.qq.com")
class WechatScraper(BaseScraper):
    """微信公众号文章爬虫 - 通过搜狗微信搜索"""

    site_name = "微信公众号"

    async def fetch_list(self, url: str) -> List[str]:
        keyword = "景区 二消 游乐项目"
        search_url = (
            f"https://weixin.sogou.com/weixin"
            f"?type=2&query={quote(keyword)}&ie=utf8"
        )
        soup = await self.fetch_page(search_url)
        if not soup:
            return []

        links = []
        for item in soup.find_all("a", href=True):
            href = item["href"]
            if "mp.weixin.qq.com" in href:
                links.append(href)
        return list(set(links))[:30]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        title = ""
        h1 = soup.find("h1", class_="rich_media_title")
        if h1:
            title = h1.get_text(strip=True)

        description = ""
        content = soup.find("div", id="js_content")
        if content:
            description = content.get_text(strip=True)

        images = []
        for img in soup.find_all("img", attrs={"data-src": True}):
            src = img.get("data-src", "")
            if src and "http" in src:
                images.append(src)

        full_text = soup.get_text()

        return ScrapedProduct(
            title=title or "微信文章",
            description=description[:2000],
            source_url=url,
            image_urls=images[:10],
            tags=self._extract_keywords(title, full_text),
            contact_phone=self.extract_phone(full_text),
            contact_wechat=self.extract_wechat(full_text),
        )


# ============================================================
# 淘宝/1688 搜索爬虫 - 搜索景区游乐设备供应商
# ============================================================
@register_scraper("taobao.com")
@register_scraper("tmall.com")
class TaobaoScraper(BaseScraper):
    """淘宝搜索爬虫 - 搜索景区游乐设备产品"""

    site_name = "淘宝"

    async def fetch_list(self, url: str) -> List[str]:
        keyword = "景区游乐设备"
        search_url = f"https://s.taobao.com/search?q={quote(keyword)}&s=0"
        soup = await self.fetch_page(search_url)
        if not soup:
            return []

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "item.taobao.com" in href or "detail.tmall.com" in href:
                links.append(href)
        return list(set(links))[:20]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        title = ""
        h1 = soup.find("h1") or soup.find("title")
        if h1:
            title = h1.get_text(strip=True)

        description = ""
        desc_div = soup.find("div", class_="attributes") or soup.find("div", id="description")
        if desc_div:
            description = desc_div.get_text(strip=True)

        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if "http" in src and "img.alicdn.com" in src:
                if not any(k in src for k in ["icon", "logo", "80x80", "40x40"]):
                    images.append("https:" + src if src.startswith("//") else src)

        # 尝试提取店铺名称
        shop_name = ""
        shop_el = soup.find("a", class_="shop-name") or soup.find("span", class_="shop-name")
        if shop_el:
            shop_name = shop_el.get_text(strip=True)

        full_text = soup.get_text()

        return ScrapedProduct(
            title=title or "淘宝产品",
            description=f"店铺: {shop_name}\n{description[:1500]}" if shop_name else description[:2000],
            source_url=url,
            image_urls=images[:10],
            tags=["淘宝供应商", "景区设备"] + self._extract_keywords(title, full_text),
        )


# ============================================================
# 小红书爬虫 - 搜索景区项目种草笔记
# ============================================================
@register_scraper("xiaohongshu.com")
@register_scraper("xhslink.com")
class XiaohongshuScraper(BaseScraper):
    """小红书爬虫 - 搜索景区二消项目种草内容"""

    site_name = "小红书"

    async def fetch_list(self, url: str) -> List[str]:
        keyword = "景区游乐项目"
        search_url = (
            f"https://www.xiaohongshu.com/search_result?"
            f"keyword={quote(keyword)}&source=web_search_result_notes"
        )
        soup = await self.fetch_page(search_url)
        if not soup:
            return []

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/explore/" in href or "/discovery/item/" in href:
                full = urljoin("https://www.xiaohongshu.com", href)
                links.append(full)
        return list(set(links))[:30]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        title = ""
        title_el = soup.find("div", id="detail-title") or soup.find("title")
        if title_el:
            title = title_el.get_text(strip=True)

        description = ""
        desc_el = soup.find("div", id="detail-desc") or soup.find("div", class_="note-content")
        if desc_el:
            description = desc_el.get_text(strip=True)

        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if "http" in src and "xhscdn.com" in src:
                images.append(src)

        full_text = soup.get_text()

        return ScrapedProduct(
            title=title or "小红书笔记",
            description=description[:2000],
            source_url=url,
            image_urls=images[:10],
            tags=["小红书种草", "景区打卡"] + self._extract_keywords(title, full_text),
            contact_wechat=self.extract_wechat(full_text),
            contact_phone=self.extract_phone(full_text),
        )


# ============================================================
# 抖音爬虫 - 通过搜索页获取视频内容
# ============================================================
@register_scraper("douyin.com")
@register_scraper("iesdouyin.com")
class DouyinScraper(BaseScraper):
    """抖音爬虫 - 搜索景区游乐项目短视频"""

    site_name = "抖音"

    async def fetch_list(self, url: str) -> List[str]:
        keyword = "景区游乐项目"
        search_url = (
            f"https://www.douyin.com/search/{quote(keyword)}"
            f"?type=general"
        )
        soup = await self.fetch_page(search_url)
        if not soup:
            return []

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/video/" in href or "/note/" in href:
                full = urljoin("https://www.douyin.com", href)
                links.append(full)
        return list(set(links))[:30]

    async def fetch_detail(self, url: str) -> Optional[ScrapedProduct]:
        soup = await self.fetch_page(url)
        if not soup:
            return None

        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")

        # 抖音视频封面
        og_image = soup.find("meta", property="og:image")
        images = []
        if og_image:
            images.append(og_image.get("content", ""))

        full_text = soup.get_text()

        return ScrapedProduct(
            title=title or "抖音视频",
            description=description[:2000],
            source_url=url,
            image_urls=images,
            video_urls=[url],
            tags=["抖音", "短视频"] + self._extract_keywords(title, full_text),
            contact_wechat=self.extract_wechat(full_text),
        )


# ============================================================
# 行业垂直网站爬虫 - 适合各类景区设备供应商官网
# 注册时使用域名关键字匹配
# ============================================================
INDUSTRY_DOMAINS = [
    "youle114.com",      # 游乐114
    "zgyle.com",          # 中国游乐设备网
    "youlece.com",        # 游乐设备网
    "99uu.com",           # 游乐志
    "dreamland.com.cn",   # 主题公园
    "themeandamusement.cn",
    "capa.org.cn",        # 中国游艺机游乐园协会
    "scenic.cn",          # 景区网
]

for domain in INDUSTRY_DOMAINS:
    register_scraper(domain)(type(
        f"{domain.replace('.com', '').replace('.cn', '').replace('.', '_')}Scraper",
        (BaseScraper,),
        {
            "site_name": domain,
            "fetch_list": lambda self, url: _generic_list(self, url),
            "fetch_detail": lambda self, url: _generic_detail(self, url),
        }
    ))


async def _generic_list(self, url: str) -> List[str]:
    """通用行业网站列表抓取"""
    soup = await self.fetch_page(url)
    if not soup:
        return []
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if len(text) > 6 and not href.startswith("#") and not href.startswith("javascript:"):
            full = urljoin(url, href)
            if any(kw in text for kw in ["产品", "项目", "设备", "景区", "游乐", "服务", "案例"]):
                links.add(full)
    return list(links)[:30]


async def _generic_detail(self, url: str) -> Optional[ScrapedProduct]:
    """通用行业网站详情抓取"""
    soup = await self.fetch_page(url)
    if not soup:
        return None

    title = ""
    for tag in ["h1", "h2", ".title", ".product-title", ".article-title"]:
        el = soup.select_one(tag) if tag.startswith(".") else soup.find(tag)
        if el:
            title = el.get_text(strip=True)
            break

    description = ""
    for sel in ["article", ".content", ".product-detail", ".article-content", "main"]:
        el = soup.select_one(sel) if sel.startswith(".") else soup.find(sel)
        if el:
            description = el.get_text(strip=True)
            break

    images = []
    for img in soup.find_all("img", src=True):
        src = img["src"]
        full_src = urljoin(url, src)
        if not any(k in full_src.lower() for k in ["icon", "logo", "avatar", "banner", "qr"]):
            images.append(full_src)

    full_text = soup.get_text()

    return ScrapedProduct(
        title=title or "行业产品",
        description=description[:2000],
        source_url=url,
        image_urls=images[:10],
        tags=_extract_industry_tags(title, full_text),
        contact_phone=self.extract_phone(full_text),
        contact_wechat=self.extract_wechat(full_text),
        contact_email=self.extract_email(full_text),
    )


def _extract_industry_tags(title: str, text: str) -> List[str]:
    """从文本提取行业相关标签"""
    keywords = [
        "景区", "游乐", "VR", "AR", "沉浸", "互动", "光影", "水滑道",
        "漂流", "攀岩", "索道", "观光", "露营", "帐篷", "民宿",
        "文创", "演艺", "实景", "水秀", "灯光", "打卡", "秋千",
        "滑索", "蹦极", "玻璃栈道", "网红桥", "彩虹滑道",
        "无动力", "亲子", "研学", "夜游", "灯光秀",
    ]
    combined = (title or "") + " " + (text or "")[:3000]
    return list(set(kw for kw in keywords if kw in combined))[:10]
