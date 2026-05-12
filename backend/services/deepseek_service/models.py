from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.core.time import utc_now_iso


@dataclass(frozen=True)
class AIAnalysis:
    provider: str
    model: str
    summary: str
    sentiment: str
    risk_score: int
    suggested_action: str
    key_points: list[str]
    raw_response: str = ""
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
