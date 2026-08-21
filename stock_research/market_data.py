"""Market data retrieval with a deterministic offline fallback."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from urllib.error import URLError
from urllib.request import urlopen


@dataclass(frozen=True)
class PriceBar:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


def fetch_history(symbol: str, lookback_days: int = 120) -> list[PriceBar]:
    """Fetch daily bars from Stooq, falling back to generated sample data."""
    stooq_symbol = symbol.lower() if "." in symbol else f"{symbol.lower()}.us"
    url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
    try:
        with urlopen(url, timeout=20) as response:
            payload = response.read().decode("utf-8")
        bars = _parse_stooq_csv(payload)
    except (TimeoutError, URLError, ValueError, OSError):
        bars = []
    if not bars:
        bars = _demo_history(symbol, max(lookback_days, 80))
    return bars[-lookback_days:]


def _parse_stooq_csv(payload: str) -> list[PriceBar]:
    reader = csv.DictReader(StringIO(payload))
    bars: list[PriceBar] = []
    for row in reader:
        if not row or row.get("Close") in {None, "N/D"}:
            continue
        bars.append(
            PriceBar(
                date=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(float(row["Volume"])),
            )
        )
    return bars


def _demo_history(symbol: str, days: int) -> list[PriceBar]:
    seed = sum(ord(char) for char in symbol)
    start = datetime.now(UTC).date() - timedelta(days=days * 2)
    bars: list[PriceBar] = []
    price = 80 + seed % 120
    for index in range(days * 2):
        current = start + timedelta(days=index)
        if current.weekday() >= 5:
            continue
        drift = math.sin(index / 5 + seed) * 0.9 + 0.08
        close = max(5, price + drift)
        high = max(price, close) * 1.012
        low = min(price, close) * 0.988
        volume = int(1_000_000 + (seed % 13) * 70_000 + index * 2500)
        bars.append(PriceBar(current, round(price, 2), round(high, 2), round(low, 2), round(close, 2), volume))
        price = close
    return bars[-days:]
