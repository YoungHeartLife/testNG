from __future__ import annotations

from dataclasses import asdict, dataclass, field

from backend.core.time import utc_now_iso


@dataclass(frozen=True)
class CrawledItem:
    source: str
    title: str
    url: str
    summary: str = ""
    published_at: str = ""
    crawled_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
