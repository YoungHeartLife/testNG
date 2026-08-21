"""Multi-model AI analysis clients using environment-provided API keys."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def build_prompt(symbol: str, indicators: dict[str, object]) -> str:
    return (
        "You are a cautious equity research assistant. Analyze the stock data for education only, "
        "highlight bullish and bearish evidence, risk controls, and a watchlist plan. "
        f"Symbol: {symbol}. Indicators: {json.dumps(indicators, ensure_ascii=False)}"
    )


def analyze_with_models(symbol: str, indicators: dict[str, object]) -> list[dict[str, str]]:
    prompt = build_prompt(symbol, indicators)
    results = [_openai(prompt), _anthropic(prompt), _gemini(prompt)]
    available = [result for result in results if result["status"] != "skipped"]
    if available:
        return available
    return [{"model": "local-rule-engine", "status": "ok", "content": _local_analysis(indicators)}]


def _post_json(url: str, headers: dict[str, str], body: dict[str, object]) -> str:
    request = Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8")


def _openai(prompt: str) -> dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {"model": "openai", "status": "skipped", "content": "OPENAI_API_KEY not configured"}
    try:
        raw = _post_json(
            "https://api.openai.com/v1/responses",
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            {"model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), "input": prompt},
        )
        data = json.loads(raw)
        text = data.get("output_text") or json.dumps(data.get("output", ""), ensure_ascii=False)
        return {"model": "openai", "status": "ok", "content": text}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        return {"model": "openai", "status": "error", "content": str(exc)}


def _anthropic(prompt: str) -> dict[str, str]:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"model": "anthropic", "status": "skipped", "content": "ANTHROPIC_API_KEY not configured"}
    try:
        raw = _post_json(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            {"model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"), "max_tokens": 900, "messages": [{"role": "user", "content": prompt}]},
        )
        data = json.loads(raw)
        text = "\n".join(block.get("text", "") for block in data.get("content", []) if isinstance(block, dict))
        return {"model": "anthropic", "status": "ok", "content": text}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        return {"model": "anthropic", "status": "error", "content": str(exc)}


def _gemini(prompt: str) -> dict[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return {"model": "gemini", "status": "skipped", "content": "GEMINI_API_KEY not configured"}
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    try:
        raw = _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            {"Content-Type": "application/json"},
            {"contents": [{"parts": [{"text": prompt}]}]},
        )
        data = json.loads(raw)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"model": "gemini", "status": "ok", "content": text}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError) as exc:
        return {"model": "gemini", "status": "error", "content": str(exc)}


def _local_analysis(indicators: dict[str, object]) -> str:
    trend = indicators.get("trend")
    rsi_value = indicators.get("rsi14")
    return f"趋势为 {trend}；RSI14={rsi_value}。建议只作为观察清单，等待价格、成交量与大盘环境共振后再人工确认。"
