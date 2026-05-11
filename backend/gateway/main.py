from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.ai.agents.prompt_agent import build_ai_prompt
from backend.services.market_service.service import get_market_status
from backend.services.selector_service.service import scan_stocks

app = FastAPI(title="AI 情绪交易系统 MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def dashboard_payload() -> dict[str, object]:
    market = get_market_status()
    signals = scan_stocks(market)
    return {
        "market": market.model_dump(mode="json"),
        "selector": [signal.model_dump(mode="json") for signal in signals],
        "ai": build_ai_prompt(market, signals),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/market/status")
def market_status() -> dict[str, object]:
    return get_market_status().model_dump(mode="json")


@app.get("/api/selector/list")
def selector_list() -> list[dict[str, object]]:
    return [signal.model_dump(mode="json") for signal in scan_stocks()]


@app.get("/api/ai/signals")
def ai_signals() -> dict[str, object]:
    market = get_market_status()
    signals = scan_stocks(market)
    return build_ai_prompt(market, signals)


@app.get("/api/dashboard")
def dashboard() -> dict[str, object]:
    return dashboard_payload()


@app.websocket("/ws/realtime")
async def realtime(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(dashboard_payload())
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        return
