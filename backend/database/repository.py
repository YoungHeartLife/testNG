from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from backend.core.time import utc_now_iso
from backend.services.crawler_service.models import CrawledItem
from backend.services.decision_service.models import StrategyDecision
from backend.services.deepseek_service.models import AIAnalysis
from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class TradingRepository:
    """SQLite persistence for hourly scans, AI analysis and notifications."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_db(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    def create_scan_run(self, *, started_at: str, data_source: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO scan_runs (started_at, finished_at, data_source, status, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (started_at, started_at, data_source, "running", ""),
            )
            return int(cursor.lastrowid)

    def finish_scan_run(self, scan_run_id: int, *, status: str, message: str = "") -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE scan_runs SET finished_at = ?, status = ?, message = ? WHERE id = ?",
                (utc_now_iso(), status, message, scan_run_id),
            )

    def save_market_status(self, scan_run_id: int, market: MarketStatus) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO market_status (
                  scan_run_id, market_status, up_count, down_count, flat_count,
                  limit_up, limit_down, broken_limit_up, broken_limit_rate,
                  risk_level, allow_buy, prompt, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_run_id,
                    market.market_status,
                    market.up_count,
                    market.down_count,
                    market.flat_count,
                    market.limit_up,
                    market.limit_down,
                    market.broken_limit_up,
                    market.broken_limit_rate,
                    market.risk_level,
                    int(market.allow_buy),
                    market.prompt,
                    market.updated_at,
                ),
            )

    def save_crawled_items(self, scan_run_id: int, items: Iterable[CrawledItem]) -> None:
        rows = [
            (scan_run_id, item.source, item.title, item.url, item.summary, item.published_at, item.crawled_at)
            for item in items
        ]
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO crawled_items (
                  scan_run_id, source, title, url, summary, published_at, crawled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def save_ai_analysis(self, scan_run_id: int, analysis: AIAnalysis) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO ai_analysis (
                  scan_run_id, provider, model, summary, sentiment, risk_score,
                  suggested_action, key_points_json, raw_response, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_run_id,
                    analysis.provider,
                    analysis.model,
                    analysis.summary,
                    analysis.sentiment,
                    analysis.risk_score,
                    analysis.suggested_action,
                    json.dumps(analysis.key_points, ensure_ascii=False),
                    analysis.raw_response,
                    analysis.created_at,
                ),
            )

    def save_signals(self, scan_run_id: int, signals: Iterable[StockSignal]) -> None:
        rows = [
            (
                scan_run_id,
                signal.stock,
                signal.name,
                signal.score,
                signal.signal_type,
                json.dumps(signal.factors, ensure_ascii=False),
                signal.explanation,
                signal.updated_at,
            )
            for signal in signals
        ]
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO ai_signals (
                  scan_run_id, stock_code, stock_name, score, signal_type,
                  factors_json, explanation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def save_decision(self, scan_run_id: int, decision: StrategyDecision) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO strategy_decisions (
                  scan_run_id, action, allow_buy, position, risk_score, reasons_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_run_id,
                    decision.action,
                    int(decision.allow_buy),
                    decision.position,
                    decision.risk_score,
                    json.dumps(decision.reasons, ensure_ascii=False),
                    decision.created_at,
                ),
            )

    def save_notification(
        self,
        scan_run_id: int,
        *,
        channel: str,
        status: str,
        payload: dict[str, object],
        error: str = "",
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO notifications (scan_run_id, channel, status, payload_json, error, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (scan_run_id, channel, status, json.dumps(payload, ensure_ascii=False), error, utc_now_iso()),
            )

    def latest_dashboard(self) -> dict[str, object] | None:
        with self.connect() as connection:
            run = connection.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT 1").fetchone()
            if run is None:
                return None
            market = connection.execute(
                "SELECT * FROM market_status WHERE scan_run_id = ? ORDER BY id DESC LIMIT 1",
                (run["id"],),
            ).fetchone()
            signals = connection.execute(
                "SELECT * FROM ai_signals WHERE scan_run_id = ? ORDER BY score DESC, id ASC",
                (run["id"],),
            ).fetchall()
            crawled = connection.execute(
                "SELECT * FROM crawled_items WHERE scan_run_id = ? ORDER BY id ASC",
                (run["id"],),
            ).fetchall()
            ai = connection.execute(
                "SELECT * FROM ai_analysis WHERE scan_run_id = ? ORDER BY id DESC LIMIT 1",
                (run["id"],),
            ).fetchone()
            decision = connection.execute(
                "SELECT * FROM strategy_decisions WHERE scan_run_id = ? ORDER BY id DESC LIMIT 1",
                (run["id"],),
            ).fetchone()
            notifications = connection.execute(
                "SELECT * FROM notifications WHERE scan_run_id = ? ORDER BY id ASC",
                (run["id"],),
            ).fetchall()
        return {
            "run": dict(run),
            "market": dict(market) if market else None,
            "signals": [dict(row) for row in signals],
            "crawled_items": [dict(row) for row in crawled],
            "ai_analysis": dict(ai) if ai else None,
            "decision": dict(decision) if decision else None,
            "notifications": [dict(row) for row in notifications],
        }
