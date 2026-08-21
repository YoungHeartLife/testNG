"""CLI entry point for the daily stock research workflow."""

from __future__ import annotations

from pathlib import Path

from .ai_clients import analyze_with_models
from .config import load_settings
from .emailer import send_report
from .indicators import summarize_indicators
from .market_data import fetch_history
from .report import markdown_to_html, render_markdown


def run() -> Path:
    settings = load_settings()
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, object]] = []
    for symbol in settings.symbols:
        bars = fetch_history(symbol, settings.lookback_days)
        indicators = summarize_indicators(bars)
        analysis = analyze_with_models(symbol, indicators)
        items.append({"symbol": symbol, "indicators": indicators, "analysis": analysis})
    markdown = render_markdown(items)
    html = markdown_to_html(markdown)
    markdown_path = output_dir / "daily_stock_report.md"
    html_path = output_dir / "daily_stock_report.html"
    markdown_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    send_report(settings, "Daily Stock AI Research Report", markdown, html)
    return markdown_path


if __name__ == "__main__":
    print(run())
