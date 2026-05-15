from __future__ import annotations

import os
from datetime import datetime, timedelta
from importlib import import_module, util
from typing import Any

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


def _tushare_available() -> bool:
    return util.find_spec("tushare") is not None


def _recent_trade_dates(days: int = 12) -> list[str]:
    today = datetime.now()
    return [(today - timedelta(days=offset)).strftime("%Y%m%d") for offset in range(days)]


def _load_tushare_candidates(limit: int = 80) -> list[dict[str, Any]]:
    """Load a small A-share candidate set from TuShare when TUSHARE_TOKEN is configured.

    The adapter is intentionally defensive: if TuShare is unavailable, the token is
    missing, quota is insufficient, or the latest trade date is not returned, the
    selector falls back to the built-in demo universe so the MVP remains usable.
    """
    token = os.getenv("TUSHARE_TOKEN")
    if not token or not _tushare_available():
        return []

    ts = import_module("tushare")
    try:
        ts.set_token(token)
        pro = ts.pro_api(token)
        for trade_date in _recent_trade_dates():
            daily_basic = pro.daily_basic(
                trade_date=trade_date,
                fields="ts_code,close,turnover_rate,volume_ratio,total_mv",
            )
            daily = pro.daily(trade_date=trade_date, fields="ts_code,pct_chg,vol,amount,high,low,open,close")
            if daily_basic.empty or daily.empty:
                continue
            merged = daily.merge(daily_basic, on="ts_code", how="left").head(limit)
            rows: list[dict[str, Any]] = []
            for row in merged.to_dict("records"):
                pct = float(row.get("pct_chg") or 0)
                volume_ratio = float(row.get("volume_ratio") or 0)
                high = float(row.get("high") or 0)
                close = float(row.get("close") or 0)
                low = float(row.get("low") or 0)
                open_price = float(row.get("open") or 0)
                upper_shadow = high - max(open_price, close)
                lower_shadow = min(open_price, close) - low
                rows.append(
                    {
                        "code": str(row.get("ts_code", "")).split(".")[0],
                        "name": str(row.get("ts_code", "")),
                        "change_pct": pct,
                        "recent_limit_up": pct >= 9.8,
                        "volume_breakout": volume_ratio >= 1.8,
                        "long_upper_shadow": upper_shadow > max(lower_shadow, 0) * 1.5 and volume_ratio >= 1.5,
                        "shrink_volume_resilient": -2 <= pct <= 2 and volume_ratio <= 0.9,
                        "first_to_second": pct > 0 and float(row.get("total_mv") or 10**9) < 11_000_000,
                    }
                )
            return rows
    except Exception:
        return []
    return []


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

    universe = _load_tushare_candidates() or DEMO_STOCKS

    for stock in universe:
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
