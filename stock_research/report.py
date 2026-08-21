"""Report rendering utilities."""

from __future__ import annotations

from datetime import UTC, datetime
from html import escape


def render_markdown(items: list[dict[str, object]]) -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Daily Stock AI Research Report", "", f"Generated: {generated_at}", "", "> Educational research only. Not investment advice.", ""]
    for item in items:
        lines.extend([f"## {item['symbol']}", "", "### Indicators", ""])
        indicators = item["indicators"]
        if isinstance(indicators, dict):
            for key, value in indicators.items():
                lines.append(f"- **{key}**: {value}")
        lines.extend(["", "### AI / Rule Analysis", ""])
        for result in item["analysis"]:
            lines.extend([f"#### {result['model']} ({result['status']})", "", str(result["content"]), ""])
    return "\n".join(lines)


def markdown_to_html(markdown: str) -> str:
    body = "\n".join(f"<p>{escape(line)}</p>" if line else "" for line in markdown.splitlines())
    return f"<html><body>{body}</body></html>"
