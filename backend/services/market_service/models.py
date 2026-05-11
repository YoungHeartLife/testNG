from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class MarketStatus(BaseModel):
    market_status: str = Field(..., description="Human-readable market phase")
    up_count: int
    down_count: int
    limit_up: int
    limit_down: int
    broken_limit_up: int
    broken_limit_rate: float
    risk_level: RiskLevel
    allow_buy: bool
    prompt: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
