"""Configuration helpers for the stock research workflow."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    symbols: list[str]
    lookback_days: int
    output_dir: str
    email_enabled: bool
    email_to: str
    email_from: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str


def load_settings() -> Settings:
    symbols = [item.strip().upper() for item in os.getenv("STOCK_SYMBOLS", "AAPL,MSFT,NVDA").split(",") if item.strip()]
    return Settings(
        symbols=symbols,
        lookback_days=int(os.getenv("LOOKBACK_DAYS", "120")),
        output_dir=os.getenv("REPORT_OUTPUT_DIR", "reports"),
        email_enabled=os.getenv("EMAIL_ENABLED", "false").lower() == "true",
        email_to=os.getenv("EMAIL_TO", ""),
        email_from=os.getenv("EMAIL_FROM", ""),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
    )
