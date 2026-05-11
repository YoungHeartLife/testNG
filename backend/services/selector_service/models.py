from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class StockSignal(BaseModel):
    stock: str = Field(..., description="A-share stock code")
    name: str
    score: float = Field(..., ge=0, le=100)
    factors: list[str]
    explanation: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
