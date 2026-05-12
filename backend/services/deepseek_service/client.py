from __future__ import annotations

import json
import urllib.error
import urllib.request

from backend.services.crawler_service.models import CrawledItem
from backend.services.deepseek_service.models import AIAnalysis
from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal


class DeepSeekAnalyzer:
    """DeepSeek chat-completions analyzer with deterministic local fallback."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: int = 30,
        enabled: bool = True,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled and bool(api_key)

    def analyze(
        self,
        *,
        market: MarketStatus,
        signals: list[StockSignal],
        crawled_items: list[CrawledItem],
    ) -> AIAnalysis:
        if not self.enabled:
            return self._fallback_analysis(market, signals, crawled_items, reason="DeepSeek API key not configured")

        prompt = self._build_prompt(market, signals, crawled_items)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是A股情绪交易风控分析师。只输出严格JSON，不要Markdown。"
                        "必须遵循：环境 > 情绪 > 个股 > 技术。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
            content = json.loads(body)["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return AIAnalysis(
                provider="deepseek",
                model=self.model,
                summary=str(parsed.get("summary", ""))[:1000],
                sentiment=str(parsed.get("sentiment", "neutral")),
                risk_score=max(0, min(100, int(parsed.get("risk_score", 50)))),
                suggested_action=str(parsed.get("suggested_action", "watch")),
                key_points=[str(item) for item in parsed.get("key_points", [])][:8],
                raw_response=content[:4000],
            )
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
            return self._fallback_analysis(market, signals, crawled_items, reason=f"DeepSeek failed: {exc}")

    def _build_prompt(
        self,
        market: MarketStatus,
        signals: list[StockSignal],
        crawled_items: list[CrawledItem],
    ) -> str:
        market_payload = market.to_dict()
        signal_payload = [signal.to_dict() for signal in signals[:10]]
        crawled_payload = [item.to_dict() for item in crawled_items[:10]]
        return json.dumps(
            {
                "task": "结合爬取数据、市场环境和策略候选股，给出交易情绪诊断。",
                "required_json_schema": {
                    "summary": "一句话诊断",
                    "sentiment": "positive|neutral|negative",
                    "risk_score": "0-100，越高风险越大",
                    "suggested_action": "buy_light|watch|reduce|clear",
                    "key_points": ["关键依据1", "关键依据2"],
                },
                "market": market_payload,
                "signals": signal_payload,
                "crawled_items": crawled_payload,
                "rules": [
                    "4000家下跌或high风险时必须clear/reduce，不允许开仓",
                    "medium风险只允许轻仓低吸，不允许追高",
                    "没有高分候选时建议watch",
                    "优先解释环境和情绪，再解释个股因子",
                ],
            },
            ensure_ascii=False,
        )

    def _fallback_analysis(
        self,
        market: MarketStatus,
        signals: list[StockSignal],
        crawled_items: list[CrawledItem],
        *,
        reason: str,
    ) -> AIAnalysis:
        risk_score = {"low": 25, "medium": 55, "high": 85}.get(market.risk_level, 50)
        if market.down_count >= 4000:
            risk_score = 95
        if crawled_items and any("失败" in item.title for item in crawled_items):
            risk_score = min(100, risk_score + 5)
        suggested_action = "buy_light" if market.allow_buy and signals and risk_score < 60 else "watch"
        if risk_score >= 80:
            suggested_action = "clear"
        elif risk_score >= 60:
            suggested_action = "reduce"
        return AIAnalysis(
            provider="local_fallback",
            model="rule-based",
            summary=f"{reason}；当前{market.market_status}，风险{market.risk_level}，候选股{len(signals)}只。",
            sentiment="negative" if risk_score >= 70 else "neutral" if risk_score >= 45 else "positive",
            risk_score=risk_score,
            suggested_action=suggested_action,
            key_points=[
                f"上涨{market.up_count}家/下跌{market.down_count}家",
                f"涨停{market.limit_up}家/跌停{market.limit_down}家",
                f"爬取上下文{len(crawled_items)}条",
                f"策略候选{len(signals)}只",
            ],
            raw_response=reason,
        )
