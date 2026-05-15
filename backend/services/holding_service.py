from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from backend.services.market_service.models import MarketStatus


class Holding(BaseModel):
    stock: str
    name: str
    cost: float
    last_price: float
    quantity: int = 0
    buy_reason: str = ""


class HoldingAdvice(BaseModel):
    stock: str
    name: str
    pnl_pct: float
    action: str
    reason: str
    stop_loss: str


class HoldingReport(BaseModel):
    items: list[HoldingAdvice]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _load_holdings() -> list[Holding]:
    raw = os.getenv("HOLDINGS_JSON")
    if raw:
        try:
            return [Holding(**item) for item in json.loads(raw)]
        except Exception:
            return []

    path = Path(os.getenv("HOLDINGS_FILE", "data/holdings.json"))
    if path.exists():
        try:
            return [Holding(**item) for item in json.loads(path.read_text(encoding="utf-8"))]
        except Exception:
            return []
    return []


def analyze_holdings(market: MarketStatus) -> HoldingReport:
    advices: list[HoldingAdvice] = []
    for holding in _load_holdings():
        pnl_pct = round((holding.last_price - holding.cost) / holding.cost * 100, 2) if holding.cost else 0.0
        if market.down_count >= 4000:
            action = "清仓"
            reason = "大盘触发 ≥4000 家下跌清仓规则。"
        elif market.down_count >= 3000:
            action = "至少减半"
            reason = "大盘触发 ≥3000 家下跌先撤退规则。"
        elif pnl_pct > 0:
            action = "锁定盈利/条件单保护"
            reason = "短线盈利必须卖，不等待回调；再强可按弱转强买回。"
        elif pnl_pct <= -5:
            action = "复核买入理由，破位止损"
            reason = "亏损扩大，必须检查是否破买入理由。"
        else:
            action = "持有观察"
            reason = "未触发大盘硬风控，继续看均价线、开盘价和量价。"
        advices.append(
            HoldingAdvice(
                stock=holding.stock,
                name=holding.name,
                pnl_pct=pnl_pct,
                action=action,
                reason=reason,
                stop_loss="破买入理由/放量下跌无反弹/10 分钟无反弹即卖",
            )
        )
    return HoldingReport(items=advices)
