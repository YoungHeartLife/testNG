from __future__ import annotations

from backend.ai.factor_engine.rules import detect_factors, score_stock
from backend.services.market_service.models import MarketStatus
from backend.services.market_service.service import get_market_status
from backend.services.selector_service.models import StockSignal

DEMO_STOCKS = [
    {
        "code": "000001",
        "name": "平安银行",
        "change_pct": 2.4,
        "recent_limit_up": True,
        "volume_breakout": True,
        "shrink_volume_resilient": True,
    },
    {
        "code": "600519",
        "name": "贵州茅台",
        "change_pct": -0.6,
        "shrink_volume_resilient": True,
    },
    {
        "code": "002594",
        "name": "比亚迪",
        "change_pct": 5.2,
        "volume_breakout": True,
        "long_upper_shadow": True,
    },
    {
        "code": "300750",
        "name": "宁德时代",
        "change_pct": 1.1,
        "recent_limit_up": True,
        "first_to_second": True,
        "shrink_volume_resilient": True,
    },
]


def _risk_multiplier(market: MarketStatus) -> float:
    if market.risk_level == "high":
        return 0.55
    if market.risk_level == "medium":
        return 0.85
    return 1.0


def scan_stocks(market: MarketStatus | None = None) -> list[StockSignal]:
    """Scan stocks using MVP manual factors and explain each selected candidate."""
    current_market = market or get_market_status()
    multiplier = _risk_multiplier(current_market)
    signals: list[StockSignal] = []

    for stock in DEMO_STOCKS:
        factors = detect_factors(stock)
        if not factors:
            continue
        score = round(score_stock(stock, factors) * multiplier, 2)
        if score < 55:
            continue
        explanation = "、".join(factors)
        signals.append(
            StockSignal(
                stock=stock["code"],
                name=stock["name"],
                score=score,
                factors=factors,
                explanation=f"命中{explanation}；遵循环境优先，当前{current_market.market_status}。",
            )
        )

    return sorted(signals, key=lambda item: item.score, reverse=True)
