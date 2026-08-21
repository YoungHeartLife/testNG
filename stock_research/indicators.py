"""Technical indicator calculations."""

from __future__ import annotations

from .market_data import PriceBar


def sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def rsi(values: list[float], window: int = 14) -> float | None:
    if len(values) <= window:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[-window - 1 : -1], values[-window:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    average_gain = sum(gains) / window
    average_loss = sum(losses) / window
    if average_loss == 0:
        return 100.0
    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def summarize_indicators(bars: list[PriceBar]) -> dict[str, float | str | None]:
    closes = [bar.close for bar in bars]
    latest = bars[-1]
    previous_close = closes[-2] if len(closes) > 1 else latest.close
    ma20 = sma(closes, 20)
    ma50 = sma(closes, 50)
    change_pct = ((latest.close - previous_close) / previous_close) * 100 if previous_close else 0
    trend = "bullish" if ma20 and ma50 and latest.close > ma20 > ma50 else "neutral"
    if ma20 and ma50 and latest.close < ma20 < ma50:
        trend = "bearish"
    return {
        "date": latest.date.isoformat(),
        "close": round(latest.close, 2),
        "change_pct": round(change_pct, 2),
        "sma20": round(ma20, 2) if ma20 else None,
        "sma50": round(ma50, 2) if ma50 else None,
        "rsi14": round(rsi(closes), 2) if rsi(closes) is not None else None,
        "volume": latest.volume,
        "trend": trend,
    }
