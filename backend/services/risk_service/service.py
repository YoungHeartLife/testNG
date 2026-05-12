from __future__ import annotations

from backend.services.market_service.models import MarketStatus


def allow_open_position(market: MarketStatus) -> bool:
    """Hard risk rule: 4000 decliners or high risk blocks new buys."""
    return market.down_count < 4000 and market.risk_level != "high"


def risk_tip(market: MarketStatus) -> str:
    if market.down_count >= 4000:
        return "下跌家数超过 4000，触发清仓/空仓风控。"
    if market.risk_level == "high":
        return "市场高风险，禁止追高和新增开仓。"
    if market.risk_level == "medium":
        return "中等风险，仅允许轻仓低吸强势股。"
    return "风险较低，可按计划小仓试错，仍需设置止损。"
