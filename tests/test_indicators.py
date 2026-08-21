from datetime import date, timedelta

from stock_research.indicators import summarize_indicators
from stock_research.market_data import PriceBar


def test_summarize_indicators_returns_expected_keys():
    bars = [PriceBar(date(2026, 1, 1) + timedelta(days=i), 100 + i, 101 + i, 99 + i, 100 + i, 1000 + i) for i in range(60)]

    summary = summarize_indicators(bars)

    assert summary["close"] == 159
    assert summary["sma20"] == 149.5
    assert summary["sma50"] == 134.5
    assert summary["trend"] == "bullish"
