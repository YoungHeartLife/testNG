from __future__ import annotations

import json
import urllib.request

from backend.services.decision_service.models import StrategyDecision
from backend.services.deepseek_service.models import AIAnalysis
from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal


class RealtimeNotifier:
    """Notify immediately after each scan via terminal and optional webhook."""

    def __init__(self, *, webhook_url: str = "", enabled: bool = True, timeout_seconds: int = 10) -> None:
        self.webhook_url = webhook_url
        self.enabled = enabled
        self.timeout_seconds = timeout_seconds
        self.last_status = "skipped"
        self.last_error = ""

    def notify(
        self,
        *,
        scan_run_id: int,
        market: MarketStatus,
        signals: list[StockSignal],
        ai: AIAnalysis,
        decision: StrategyDecision,
    ) -> dict[str, object]:
        payload = {
            "scan_run_id": scan_run_id,
            "title": "AI情绪交易系统策略扫描完成",
            "market_status": market.market_status,
            "risk_level": market.risk_level,
            "allow_buy": decision.allow_buy,
            "action": decision.action,
            "position": decision.position,
            "ai_provider": ai.provider,
            "ai_risk_score": ai.risk_score,
            "ai_summary": ai.summary,
            "top_signal": signals[0].to_dict() if signals else None,
            "reasons": decision.reasons,
        }
        if not self.enabled:
            self.last_status = "disabled"
            return payload
        if not self.webhook_url:
            self.last_status = "console_only"
            return payload
        try:
            request = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response.read()
            self.last_status = "sent"
            self.last_error = ""
        except Exception as exc:
            self.last_status = "failed"
            self.last_error = str(exc)
        return payload
