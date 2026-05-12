from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _csv_env(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the terminal-first backend scanner."""

    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/ai_trading.sqlite3"))
    scan_interval_seconds: int = int(os.getenv("SCAN_INTERVAL_SECONDS", "3600"))
    top_n: int = int(os.getenv("TOP_N", "20"))
    use_demo_data: bool = os.getenv("USE_DEMO_DATA", "auto").lower() == "true"
    crawl_urls: list[str] = field(default_factory=lambda: _csv_env("CRAWL_URLS"))
    crawl_limit: int = int(os.getenv("CRAWL_LIMIT", "10"))
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    deepseek_enabled: bool = os.getenv("DEEPSEEK_ENABLED", "true").lower() != "false"
    notify_enabled: bool = os.getenv("NOTIFY_ENABLED", "true").lower() != "false"
    notify_webhook_url: str = os.getenv("NOTIFY_WEBHOOK_URL", "")


def get_settings() -> Settings:
    return Settings()
