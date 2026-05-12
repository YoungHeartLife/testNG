from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

from backend.core.time import utc_now_iso

RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class StockSnapshot:
    code: str
    name: str
    change_pct: float
    price: float = 0.0
    high: float = 0.0
    low: float = 0.0
    open_price: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    amplitude: float = 0.0
    turnover: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MarketStatus:
    market_status: str
    up_count: int
    down_count: int
    flat_count: int
    limit_up: int
    limit_down: int
    broken_limit_up: int
    broken_limit_rate: float
    risk_level: RiskLevel
    allow_buy: bool
    prompt: str
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
