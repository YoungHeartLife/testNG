from __future__ import annotations

import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse
from xml.etree import ElementTree

from backend.services.crawler_service.models import CrawledItem
from backend.services.market_service.models import MarketStatus


class _HTMLTitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta":
            attr = {key.lower(): value or "" for key, value in attrs}
            if attr.get("name", "").lower() == "description" or attr.get("property", "").lower() == "og:description":
                self.description = attr.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data.strip())

    @property
    def title(self) -> str:
        return " ".join(part for part in self.title_parts if part).strip()


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class NewsCrawler:
    """Small stdlib crawler for URLs/RSS feeds used as DeepSeek context."""

    def __init__(self, urls: list[str], *, timeout_seconds: int = 8, limit: int = 10) -> None:
        self.urls = [url for url in urls if url]
        self.timeout_seconds = timeout_seconds
        self.limit = limit

    def crawl(self, market: MarketStatus | None = None) -> list[CrawledItem]:
        items: list[CrawledItem] = []
        for url in self.urls:
            if len(items) >= self.limit:
                break
            try:
                items.extend(self._crawl_url(url)[: self.limit - len(items)])
            except Exception as exc:
                items.append(
                    CrawledItem(
                        source="crawler_error",
                        title=f"抓取失败：{urlparse(url).netloc or url}",
                        url=url,
                        summary=str(exc)[:300],
                    )
                )
        if items:
            return items[: self.limit]
        return self._fallback_items(market)[: self.limit]

    def _crawl_url(self, url: str) -> list[CrawledItem]:
        request = urllib.request.Request(url, headers={"User-Agent": "ai-trading-scanner/1.0"})
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(1_000_000).decode("utf-8", errors="ignore")
        if "xml" in content_type or "rss" in content_type or "<rss" in body[:500].lower():
            return self._parse_rss(url, body)
        return [self._parse_html(url, body)]

    def _parse_rss(self, url: str, body: str) -> list[CrawledItem]:
        root = ElementTree.fromstring(body)
        parsed = urlparse(url)
        source = parsed.netloc or url
        items: list[CrawledItem] = []
        for element in root.findall(".//item"):
            title = _clean_text(element.findtext("title") or "")
            link = _clean_text(element.findtext("link") or url)
            summary = _clean_text(element.findtext("description") or "")
            published_at = _clean_text(element.findtext("pubDate") or "")
            if title:
                items.append(
                    CrawledItem(
                        source=source,
                        title=title,
                        url=link,
                        summary=summary[:500],
                        published_at=published_at,
                    )
                )
        return items

    def _parse_html(self, url: str, body: str) -> CrawledItem:
        parser = _HTMLTitleParser()
        parser.feed(body)
        source = urlparse(url).netloc or url
        title = _clean_text(parser.title or source)
        summary = _clean_text(parser.description)
        if not summary:
            text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", body, flags=re.I)
            text = re.sub(r"<[^>]+>", " ", text)
            summary = _clean_text(text)[:500]
        return CrawledItem(source=source, title=title, url=url, summary=summary[:500])

    def _fallback_items(self, market: MarketStatus | None) -> list[CrawledItem]:
        if market is None:
            return [
                CrawledItem(
                    source="local_context",
                    title="未配置爬取URL，使用本地市场上下文",
                    url="local://market-context",
                    summary="请设置 CRAWL_URLS 或使用 --crawl-url 添加财经新闻、公告或情绪源。",
                )
            ]
        return [
            CrawledItem(
                source="local_market_context",
                title=f"本地市场快照：{market.market_status} / {market.risk_level}",
                url="local://market-context",
                summary=(
                    f"上涨{market.up_count}家，下跌{market.down_count}家，涨停{market.limit_up}家，"
                    f"跌停{market.limit_down}家，炸板率{market.broken_limit_rate:.2%}，"
                    f"是否允许开仓：{market.allow_buy}。"
                ),
            )
        ]
