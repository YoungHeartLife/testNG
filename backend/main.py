from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from backend.core.config import Settings, get_settings
from backend.database.repository import TradingRepository
from backend.services.crawler_service.models import CrawledItem
from backend.services.decision_service.models import StrategyDecision
from backend.services.deepseek_service.models import AIAnalysis
from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal
from backend.services.strategy_service.scanner import HourlyStrategyScanner
from backend.terminal import (
    render_ai,
    render_crawled_items,
    render_decision,
    render_deepseek,
    render_json,
    render_market,
    render_signals,
)


def _settings_from_args(args: argparse.Namespace) -> Settings:
    base = get_settings()
    crawl_urls = list(base.crawl_urls)
    if getattr(args, "crawl_url", None):
        crawl_urls.extend(args.crawl_url)
    return Settings(
        database_path=Path(args.database) if args.database else base.database_path,
        scan_interval_seconds=args.interval,
        top_n=args.top,
        use_demo_data=args.demo or base.use_demo_data,
        crawl_urls=crawl_urls,
        crawl_limit=args.crawl_limit,
        deepseek_api_key=args.deepseek_api_key or base.deepseek_api_key,
        deepseek_base_url=args.deepseek_base_url or base.deepseek_base_url,
        deepseek_model=args.deepseek_model or base.deepseek_model,
        deepseek_enabled=not args.no_deepseek and base.deepseek_enabled,
        notify_enabled=not args.no_notify and base.notify_enabled,
        notify_webhook_url=args.notify_webhook_url or base.notify_webhook_url,
    )


def _scanner(args: argparse.Namespace) -> HourlyStrategyScanner:
    settings = _settings_from_args(args)
    return HourlyStrategyScanner(settings, TradingRepository(settings.database_path))


def _signals_from_payload(result: dict[str, object]) -> list[StockSignal]:
    return [StockSignal(**signal) for signal in result.get("signals", [])]


def _print_result(result: dict[str, object], *, output_json: bool) -> None:
    if output_json:
        print(render_json(result))
        return

    market = MarketStatus(**result["market"])
    signals = _signals_from_payload(result)
    crawled_items = [CrawledItem(**item) for item in result.get("crawled_items", [])]
    deepseek_payload = result["ai"]["deepseek"]
    decision_payload = result["decision"]
    deepseek = AIAnalysis(**deepseek_payload)
    decision = StrategyDecision(**decision_payload)

    print(render_market(market, data_source=str(result["data_source"])))
    print(render_crawled_items(crawled_items))
    print(render_deepseek(deepseek))
    print(render_decision(decision))
    print(render_signals(signals))
    print(render_ai(result["ai"]))
    notification = result.get("notification", {})
    print(f"实时通知：{notification.get('title', '已生成')} | 动作={notification.get('action')} | 仓位={notification.get('position')}")
    print(f"SQLite已写入：scan_run_id={result['scan_run_id']}\n")


def scan_command(args: argparse.Namespace) -> None:
    scanner = _scanner(args)
    if args.loop:
        print(f"启动1小时策略扫描循环，每 {args.interval} 秒执行一次。按 Ctrl+C 停止。")
        while True:
            result = scanner.scan_once().to_dict()
            _print_result(result, output_json=args.json)
            time.sleep(args.interval)
    else:
        result = scanner.scan_once().to_dict()
        _print_result(result, output_json=args.json)


def latest_command(args: argparse.Namespace) -> None:
    settings = get_settings()
    database_path = Path(args.database) if args.database else settings.database_path
    repository = TradingRepository(database_path)
    repository.init_db()
    payload = repository.latest_dashboard()
    if payload is None:
        print("暂无扫描结果，请先运行：python -m backend.main scan")
        return
    print(render_json(payload))


def _add_common_scan_args(scan: argparse.ArgumentParser) -> None:
    scan.add_argument("--loop", action="store_true", help="循环执行，默认每1小时扫描一次")
    scan.add_argument("--interval", type=int, default=3600, help="循环扫描间隔秒数，默认3600")
    scan.add_argument("--top", type=int, default=20, help="输出/保存前N个信号，默认20")
    scan.add_argument("--database", help="SQLite文件路径，默认data/ai_trading.sqlite3")
    scan.add_argument("--demo", action="store_true", help="强制使用演示数据，不请求AkShare")
    scan.add_argument("--json", action="store_true", help="以JSON格式输出")
    scan.add_argument("--crawl-url", action="append", default=[], help="增加一个要爬取的财经/公告/RSS URL，可重复")
    scan.add_argument("--crawl-limit", type=int, default=10, help="每轮最多保留的爬取条数，默认10")
    scan.add_argument("--deepseek-api-key", default="", help="DeepSeek API Key；也可用环境变量DEEPSEEK_API_KEY")
    scan.add_argument("--deepseek-base-url", default="", help="DeepSeek Base URL；默认https://api.deepseek.com")
    scan.add_argument("--deepseek-model", default="", help="DeepSeek模型；默认deepseek-chat")
    scan.add_argument("--no-deepseek", action="store_true", help="禁用DeepSeek，使用本地规则AI兜底")
    scan.add_argument("--notify-webhook-url", default="", help="实时通知Webhook；也可用NOTIFY_WEBHOOK_URL")
    scan.add_argument("--no-notify", action="store_true", help="禁用通知；终端输出仍保留")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI 情绪交易系统：DeepSeek + 爬取数据 + SQLite 1小时策略扫描")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="执行策略扫描")
    _add_common_scan_args(scan)
    scan.set_defaults(func=scan_command)

    latest = subparsers.add_parser("latest", help="查看SQLite中最近一次扫描结果")
    latest.add_argument("--database", help="SQLite文件路径，默认data/ai_trading.sqlite3")
    latest.set_defaults(func=latest_command)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
