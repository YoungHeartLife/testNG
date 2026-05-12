from __future__ import annotations

from dataclasses import asdict, dataclass, field

from backend.core.time import utc_now_iso


@dataclass(frozen=True)
class StockSignal:
    stock: str
    name: str
    score: float
    factors: list[str]
    explanation: str
    signal_type: str = "hourly_strategy_scan"
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
