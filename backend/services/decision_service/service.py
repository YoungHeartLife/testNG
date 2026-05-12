from __future__ import annotations

from backend.services.deepseek_service.models import AIAnalysis
from backend.services.decision_service.models import StrategyDecision
from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal


def decide_strategy(market: MarketStatus, signals: list[StockSignal], ai: AIAnalysis) -> StrategyDecision:
    reasons = [
        f"市场状态：{market.market_status} / {market.risk_level}",
        f"DeepSeek风险分：{ai.risk_score}，建议：{ai.suggested_action}",
        f"策略候选：{len(signals)}只",
    ]
    if market.down_count >= 4000 or market.risk_level == "high" or ai.risk_score >= 80:
        return StrategyDecision(
            action="clear_or_empty",
            allow_buy=False,
            position="0%",
            risk_score=ai.risk_score,
            reasons=reasons + ["触发高风险/4000家下跌/AI高风险，禁止开仓。"],
        )
    if ai.risk_score >= 60 or market.risk_level == "medium":
        return StrategyDecision(
            action="watch_or_low_absorb_only",
            allow_buy=market.allow_buy and bool(signals),
            position="<=20%",
            risk_score=ai.risk_score,
            reasons=reasons + ["中等风险，只允许低吸强势股，禁止追高。"],
        )
    if signals and market.allow_buy and ai.suggested_action in {"buy_light", "watch"}:
        return StrategyDecision(
            action="buy_light_candidates",
            allow_buy=True,
            position="<=30%",
            risk_score=ai.risk_score,
            reasons=reasons + [f"最高候选：{signals[0].name}({signals[0].stock}) {signals[0].score}分。"],
        )
    return StrategyDecision(
        action="watch",
        allow_buy=False,
        position="0%",
        risk_score=ai.risk_score,
        reasons=reasons + ["候选不足或AI未确认，等待下一轮扫描。"],
    )
