from __future__ import annotations

from dataclasses import asdict, dataclass, field

from backend.core.time import utc_now_iso


@dataclass(frozen=True)
class StrategyDecision:
    action: str
    allow_buy: bool
    position: str
    risk_score: int
    reasons: list[str]
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
