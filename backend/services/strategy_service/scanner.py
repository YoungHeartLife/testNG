from __future__ import annotations

from dataclasses import asdict, dataclass

from backend.ai.agents.prompt_agent import build_ai_prompt
from backend.core.config import Settings
from backend.core.time import utc_now_iso
from backend.database.repository import TradingRepository
from backend.services.crawler_service.service import NewsCrawler
from backend.services.decision_service.service import decide_strategy
from backend.services.deepseek_service.client import DeepSeekAnalyzer
from backend.services.market_service.data_provider import MarketDataProvider
from backend.services.market_service.service import analyze_market
from backend.services.notification_service.service import RealtimeNotifier
from backend.services.selector_service.service import scan_stocks


@dataclass(frozen=True)
class ScanResult:
    scan_run_id: int
    started_at: str
    finished_at: str
    data_source: str
    market: dict[str, object]
    signals: list[dict[str, object]]
    crawled_items: list[dict[str, object]]
    ai: dict[str, object]
    decision: dict[str, object]
    notification: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class HourlyStrategyScanner:
    """Coordinates market -> crawl -> DeepSeek -> strategy decision -> notify -> SQLite."""

    def __init__(self, settings: Settings, repository: TradingRepository) -> None:
        self.settings = settings
        self.repository = repository
        self.provider = MarketDataProvider(force_demo=settings.use_demo_data)
        self.crawler = NewsCrawler(settings.crawl_urls, limit=settings.crawl_limit)
        self.deepseek = DeepSeekAnalyzer(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
            enabled=settings.deepseek_enabled,
        )
        self.notifier = RealtimeNotifier(
            webhook_url=settings.notify_webhook_url,
            enabled=settings.notify_enabled,
        )

    def scan_once(self) -> ScanResult:
        self.repository.init_db()
        started_at = utc_now_iso()
        snapshots = self.provider.load_snapshots()
        data_source = self.provider.last_source
        scan_run_id = self.repository.create_scan_run(started_at=started_at, data_source=data_source)

        try:
            market = analyze_market(snapshots)
            crawled_items = self.crawler.crawl(market)
            signals = scan_stocks(snapshots, market, top_n=self.settings.top_n)
            deepseek_analysis = self.deepseek.analyze(
                market=market,
                signals=signals,
                crawled_items=crawled_items,
            )
            decision = decide_strategy(market, signals, deepseek_analysis)
            ai_payload = build_ai_prompt(market, signals, deepseek_analysis, decision, crawled_items)
            notification_payload = self.notifier.notify(
                scan_run_id=scan_run_id,
                market=market,
                signals=signals,
                ai=deepseek_analysis,
                decision=decision,
            )

            self.repository.save_market_status(scan_run_id, market)
            self.repository.save_crawled_items(scan_run_id, crawled_items)
            self.repository.save_ai_analysis(scan_run_id, deepseek_analysis)
            self.repository.save_signals(scan_run_id, signals)
            self.repository.save_decision(scan_run_id, decision)
            self.repository.save_notification(
                scan_run_id,
                channel="webhook" if self.settings.notify_webhook_url else "console",
                status=self.notifier.last_status,
                payload=notification_payload,
                error=self.notifier.last_error,
            )
            self.repository.finish_scan_run(scan_run_id, status="success", message=self.provider.last_error)

            return ScanResult(
                scan_run_id=scan_run_id,
                started_at=started_at,
                finished_at=utc_now_iso(),
                data_source=data_source,
                market=market.to_dict(),
                signals=[signal.to_dict() for signal in signals],
                crawled_items=[item.to_dict() for item in crawled_items],
                ai=ai_payload,
                decision=decision.to_dict(),
                notification=notification_payload,
            )
        except Exception as exc:
            self.repository.finish_scan_run(scan_run_id, status="failed", message=str(exc))
            raise
