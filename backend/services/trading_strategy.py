from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal

ActionLevel = Literal["buy_allowed", "no_buy", "half_position", "clear_all"]


class StrategyDecision(BaseModel):
    action_level: ActionLevel
    action_title: str
    position_hint: str
    buy_window: str
    hard_rules: list[str]
    risk_warnings: list[str]
    execution_checklist: list[str]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


TRADING_RULES: dict[str, list[str]] = {
    "market": [
        "≥3000 家上涨才允许买入；<3000 家上涨禁止买入。",
        "≥4000 家下跌立即清仓；≥3000 家下跌先砍半仓再判断。",
        "大盘快速跳水后 10 分钟无反弹，全部清掉。",
    ],
    "position": [
        "总资金 ÷ 10 为标准单票仓位，稳健模式可用总资金 ÷ 5。",
        "根据环境自然空仓，不刻意满仓。",
        "连亏 2 天减仓 30%～50%，连亏 3 天直接清仓并复盘。",
    ],
    "buy": [
        "只在 10:40 前或 14:40 后买入/补仓/确认。",
        "开盘冲高后只买缩量回踩均价线或开盘价支撑。",
        "冲到 9.8%/9.9% 不追，放量上穿均价线禁止买。",
    ],
    "sell": [
        "破买入理由必须止损；无反弹放量下跌必卖。",
        "盈利必须卖，若再强则按弱转强重新买回。",
        "10:40 前完成减仓或条件单，不允许幻想持仓。",
    ],
}


def decide_strategy(market: MarketStatus, signals: list[StockSignal] | None = None) -> StrategyDecision:
    candidates = signals or []
    hard_rules = [*TRADING_RULES["market"], *TRADING_RULES["buy"]]
    warnings: list[str] = []

    if market.down_count >= 4000:
        action_level: ActionLevel = "clear_all"
        title = "立即清仓 / 禁止买入"
        position = "执行 0% 仓位；先撤退，不再判断个股。"
        warnings.append("下跌家数达到 4000 家清仓线，触发最高优先级风控。")
    elif market.down_count >= 3000:
        action_level = "half_position"
        title = "先砍半仓 / 暂停新增"
        position = "先降至 50% 以下；已有盈利仓优先锁定。"
        warnings.append("下跌家数达到 3000 家撤退线，先减仓再观察。")
    elif market.up_count >= 3000 and market.allow_buy:
        action_level = "buy_allowed"
        title = "可做买入 / 只低吸不追高"
        position = "按总资金 ÷ 10 试错；稳健模式单票不超过总资金 ÷ 5。"
    else:
        action_level = "no_buy"
        title = "禁止买入 / 等待环境"
        position = "保持现金或防守仓位；只做复盘和条件单。"
        warnings.append("上涨家数未达到 3000 家，未满足唯一买入条件。")

    if market.risk_level == "high":
        warnings.append("系统风险等级为 high，禁止追高和新增开仓。")
    if market.broken_limit_rate >= 0.25:
        warnings.append(f"炸板率 {(market.broken_limit_rate * 100):.1f}% 偏高，短线接力失败风险上升。")
    if not candidates:
        warnings.append("当前无满足硬条件的重点池候选，无法解释的交易视为违规。")

    checklist = [
        "9:25 记录涨跌家数，确认是否满足 ≥3000 家上涨。",
        "9:30-9:31 记录开盘量比与是否放量下杀。",
        "9:30-10:40 仅扫描缩量回踩均价线/开盘价的买点。",
        "10:40 前完成减仓、止损或条件单。",
        "14:40 后只做确认型补仓，仍禁止追高。",
        "收盘登记买卖理由、执行度、盈亏和情绪分。",
    ]

    return StrategyDecision(
        action_level=action_level,
        action_title=title,
        position_hint=position,
        buy_window="10:40 以前为核心买点；14:40 以后仅补仓/确认。",
        hard_rules=hard_rules,
        risk_warnings=warnings,
        execution_checklist=checklist,
    )


def score_buy_point(signal: StockSignal, market: MarketStatus) -> dict[str, Any]:
    """Create an explainable intraday trading note for a selected candidate."""
    can_buy = market.up_count >= 3000 and market.down_count < 3000 and market.allow_buy
    blockers: list[str] = []
    if market.up_count < 3000:
        blockers.append("上涨家数不足 3000")
    if market.down_count >= 3000:
        blockers.append("下跌家数达到撤退线")
    if not market.allow_buy:
        blockers.append("市场风控不允许开仓")

    return {
        "stock": signal.stock,
        "name": signal.name,
        "score": signal.score,
        "trade_action": "观察缩量回踩买点" if can_buy else "仅观察，禁止买入",
        "position_plan": "标准 1/10 仓试错；触发放量下跌立即止损" if can_buy else "不新增仓位",
        "buy_conditions": [
            "10:40 前或 14:40 后",
            "回踩均价线/开盘价缩量支撑",
            "不追 9.8%/9.9%，不买放量上穿均价线",
        ],
        "sell_conditions": [
            "跌破买入理由或放量下跌无反弹",
            "盈利先锁定，弱转强再作为新交易买回",
            "10:40 前完成减仓或条件单",
        ],
        "blockers": blockers,
    }
