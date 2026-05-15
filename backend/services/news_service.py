from __future__ import annotations

from datetime import datetime, timezone
from importlib import import_module, util
from typing import Any

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str
    source: str
    published_at: str
    risk_hint: str
    url: str | None = None


OFFICIAL_SOURCES = [
    "中国证监会：https://www.csrc.gov.cn",
    "上海证券交易所：https://www.sse.com.cn",
    "深圳证券交易所：https://www.szse.cn",
    "北京证券交易所：https://www.bse.cn",
    "中国人民银行：http://www.pbc.gov.cn",
    "国家统计局：https://www.stats.gov.cn",
]


class NewsRiskReport(BaseModel):
    summary: str
    risk_level: str
    official_sources: list[str] = Field(default_factory=lambda: OFFICIAL_SOURCES.copy())
    items: list[NewsItem]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _akshare_available() -> bool:
    return util.find_spec("akshare") is not None


def _risk_hint(title: str) -> str:
    risk_keywords = ["监管", "退市", "减持", "加息", "制裁", "风险", "下调", "处罚", "问询"]
    positive_keywords = ["政策", "支持", "回购", "增持", "降准", "降息", "增长", "突破"]
    if any(keyword in title for keyword in risk_keywords):
        return "风险提示：消息含监管/流动性/信用压力关键词，降低仓位优先级。"
    if any(keyword in title for keyword in positive_keywords):
        return "机会提示：消息含政策或资金面正向关键词，但仍需等待量价确认。"
    return "中性提示：作为消息面背景，不替代涨跌家数风控。"


def fetch_official_news(limit: int = 8) -> NewsRiskReport:
    """Fetch official/major-market news with AkShare when available; fall back to curated prompts."""
    items: list[NewsItem] = []
    if _akshare_available():
        ak = import_module("akshare")
        loaders = [
            ("stock_info_global_cls", "财联社"),
            ("stock_news_main_cx", "财新/主流财经"),
        ]
        for func_name, source in loaders:
            try:
                loader = getattr(ak, func_name)
                df = loader()
                for row in df.head(limit).to_dict("records"):
                    title = str(row.get("标题") or row.get("title") or row.get("内容") or "").strip()
                    if not title:
                        continue
                    published_at = str(row.get("发布时间") or row.get("pub_time") or row.get("时间") or "")
                    url = row.get("链接") or row.get("url")
                    items.append(
                        NewsItem(
                            title=title,
                            source=source,
                            published_at=published_at,
                            risk_hint=_risk_hint(title),
                            url=str(url) if url else None,
                        )
                    )
                    if len(items) >= limit:
                        break
            except Exception:
                continue
            if len(items) >= limit:
                break

    if not items:
        fallback_titles = [
            "交易前必须优先查看证监会、交易所、央行与国家统计局等官方信息源",
            "若出现监管处罚、退市、问询、重大减持或海外风险升级，降低当日仓位",
            "若出现政策支持或流动性改善，也必须等待涨跌家数与量价共振确认",
        ]
        items = [
            NewsItem(title=title, source="内置官方新闻检查清单", published_at="待接入实时源", risk_hint=_risk_hint(title))
            for title in fallback_titles
        ]

    high_count = sum("风险提示" in item.risk_hint for item in items)
    risk_level = "high" if high_count >= 3 else "medium" if high_count else "low"
    summary = "消息面偏风险，开仓必须更谨慎。" if risk_level == "high" else "消息面需结合大盘涨跌家数确认。"
    return NewsRiskReport(summary=summary, risk_level=risk_level, items=items[:limit])
