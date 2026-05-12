from __future__ import annotations

from backend.services.market_service.models import StockSnapshot


def detect_factors(stock: StockSnapshot) -> list[str]:
    """Detect explainable hourly strategy factors from snapshot fields."""
    factors: list[str] = []

    if stock.change_pct >= 9.8:
        factors.append("最近涨停")
    if 3 <= stock.change_pct < 9.8 and stock.amount >= 300_000_000 and stock.turnover >= 3:
        factors.append("横盘突破")
    if stock.amplitude >= 8 and stock.change_pct >= 3 and stock.high > stock.price:
        factors.append("放量长上影")
    if -2 <= stock.change_pct <= 2 and stock.amount >= 100_000_000:
        factors.append("缩量抗跌")
    if 6 <= stock.change_pct < 9.8 and stock.turnover >= 5:
        factors.append("一进二预备")
    if stock.change_pct > 0:
        factors.append("强于指数")

    return factors


def score_stock(stock: StockSnapshot, factors: list[str]) -> float:
    """Score candidates with conservative environment-first factor weights."""
    base_score = 35.0
    weights = {
        "最近涨停": 16.0,
        "横盘突破": 18.0,
        "放量长上影": 9.0,
        "缩量抗跌": 14.0,
        "一进二预备": 15.0,
        "强于指数": 5.0,
    }
    score = base_score + sum(weights.get(factor, 0.0) for factor in factors)

    if stock.change_pct > 8:
        score -= 8
    if stock.amount >= 1_000_000_000:
        score += 6
    if stock.turnover > 12:
        score -= 5
    if stock.price <= 0:
        score -= 20

    return max(0.0, min(100.0, round(score, 2)))
