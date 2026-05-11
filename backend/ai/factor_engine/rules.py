from __future__ import annotations

from typing import Any


def detect_factors(stock: dict[str, Any]) -> list[str]:
    """Detect first-stage hand-written factors for explainable MVP selection."""
    factors: list[str] = []

    if stock.get("recent_limit_up"):
        factors.append("近期涨停")
    if stock.get("volume_breakout"):
        factors.append("横盘突破")
    if stock.get("long_upper_shadow"):
        factors.append("放量长上影")
    if stock.get("shrink_volume_resilient"):
        factors.append("缩量抗跌")
    if stock.get("first_to_second"):
        factors.append("一进二")

    return factors


def score_stock(stock: dict[str, Any], factors: list[str]) -> float:
    """Score stocks with environment-first conservative weighting."""
    base_score = 45.0
    weights = {
        "横盘突破": 18.0,
        "缩量抗跌": 16.0,
        "近期涨停": 12.0,
        "一进二": 14.0,
        "放量长上影": 8.0,
    }
    score = base_score + sum(weights.get(factor, 0.0) for factor in factors)

    change_pct = float(stock.get("change_pct", 0.0) or 0.0)
    if change_pct > 7:
        score -= 10
    elif -2 <= change_pct <= 4:
        score += 5

    return max(0.0, min(100.0, round(score, 2)))
