from __future__ import annotations

from backend.services.market_service.models import MarketStatus
from backend.services.risk_service.service import risk_tip
from backend.services.selector_service.models import StockSignal


def build_ai_prompt(market: MarketStatus, signals: list[StockSignal]) -> dict[str, object]:
    action = "允许轻仓试错" if market.allow_buy else "禁止开仓"
    focus = "低吸强势股" if market.allow_buy else "防守与复盘"
    text = f"当前市场：{market.market_status}\n\n{risk_tip(market)}\n\n当前适合：{focus}。\n操作建议：{action}，禁止追高。"
    return {
        "market_status": market.market_status,
        "risk_level": market.risk_level,
        "allow_buy": market.allow_buy,
        "message": text,
        "top_signals": [signal.model_dump(mode="json") for signal in signals[:5]],
    }
