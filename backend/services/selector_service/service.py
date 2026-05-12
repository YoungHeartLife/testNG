from __future__ import annotations

from backend.ai.factor_engine.rules import detect_factors, score_stock
from backend.services.market_service.models import MarketStatus, StockSnapshot
from backend.services.selector_service.models import StockSignal


def _risk_multiplier(market: MarketStatus) -> float:
    if market.risk_level == "high":
        return 0.45
    if market.risk_level == "medium":
        return 0.8
    return 1.0


def scan_stocks(
    snapshots: list[StockSnapshot],
    market: MarketStatus,
    *,
    top_n: int = 20,
) -> list[StockSignal]:
    """Run the MVP hourly selector over the current A-share snapshot list."""
    multiplier = _risk_multiplier(market)
    signals: list[StockSignal] = []

    for stock in snapshots:
        factors = detect_factors(stock)
        if len(factors) < 2:
            continue

        score = round(score_stock(stock, factors) * multiplier, 2)
        if score < 55:
            continue

        factors_text = "、".join(factors)
        signals.append(
            StockSignal(
                stock=stock.code,
                name=stock.name,
                score=score,
                factors=factors,
                explanation=(
                    f"命中{factors_text}；当前市场{market.market_status}，"
                    f"风险等级{market.risk_level}，{'允许轻仓' if market.allow_buy else '禁止开仓'}。"
                ),
            )
        )

    return sorted(signals, key=lambda item: item.score, reverse=True)[:top_n]
