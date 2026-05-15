from __future__ import annotations

from datetime import datetime, timezone
from html import escape

from pydantic import BaseModel, Field

from backend.services.holding_service import HoldingReport, analyze_holdings
from backend.services.market_service.models import MarketStatus
from backend.services.market_service.service import get_market_status
from backend.services.news_service import NewsRiskReport, fetch_official_news
from backend.services.pushplus_service import send_pushplus_report
from backend.services.selector_service.models import StockSignal
from backend.services.selector_service.service import scan_stocks
from backend.services.trading_strategy import StrategyDecision, decide_strategy, score_buy_point


class DailyTradingReport(BaseModel):
    title: str
    market: MarketStatus
    strategy: StrategyDecision
    news: NewsRiskReport
    selector: list[StockSignal]
    stock_trade_notes: list[dict[str, object]]
    holdings: HoldingReport
    html: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _pill(text: str, color: str) -> str:
    return f'<span style="display:inline-block;border-radius:999px;padding:4px 10px;background:{color};color:white;font-size:12px;margin:2px;">{escape(text)}</span>'


def render_report_html(report: DailyTradingReport) -> str:
    market = report.market
    strategy = report.strategy
    action_color = {
        "buy_allowed": "#16a34a",
        "no_buy": "#f59e0b",
        "half_position": "#f97316",
        "clear_all": "#dc2626",
    }[strategy.action_level]
    selector_html = "".join(
        f"""
        <tr>
          <td style='padding:10px;border-bottom:1px solid #e5e7eb;'><b>{escape(item.name)}</b><br><span style='color:#64748b'>{escape(item.stock)}</span></td>
          <td style='padding:10px;border-bottom:1px solid #e5e7eb;'>{item.score}</td>
          <td style='padding:10px;border-bottom:1px solid #e5e7eb;'>{''.join(_pill(factor, '#0284c7') for factor in item.factors)}</td>
          <td style='padding:10px;border-bottom:1px solid #e5e7eb;'>{escape(item.explanation)}</td>
        </tr>
        """
        for item in report.selector[:8]
    ) or "<tr><td colspan='4' style='padding:12px;color:#dc2626;'>当前无重点池候选，禁止临时起意交易。</td></tr>"
    official_html = "".join(f"<li>{escape(source)}</li>" for source in report.news.official_sources)
    news_html = "".join(
        f"<li style='margin:8px 0;'><b>{escape(item.source)}</b>：{escape(item.title)}<br><span style='color:#b45309'>{escape(item.risk_hint)}</span></li>"
        for item in report.news.items
    )
    holding_html = "".join(
        f"<li style='margin:8px 0;'><b>{escape(item.name)} {escape(item.stock)}</b>：{item.action}（{item.pnl_pct}%）— {escape(item.reason)}</li>"
        for item in report.holdings.items
    ) or "<li>未配置持仓。可通过 HOLDINGS_JSON 或 data/holdings.json 接入持仓后生成个股交易信息。</li>"
    checklist_html = "".join(f"<li>{escape(item)}</li>" for item in strategy.execution_checklist)
    warnings_html = "".join(f"<li>{escape(item)}</li>" for item in strategy.risk_warnings) or "<li>未触发额外风险提示，但仍必须遵守禁止追高。</li>"

    return f"""
    <div style='font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;background:#0f172a;padding:20px;color:#0f172a;'>
      <div style='max-width:920px;margin:0 auto;background:#f8fafc;border-radius:24px;overflow:hidden;box-shadow:0 24px 80px rgba(15,23,42,.35);'>
        <div style='background:linear-gradient(135deg,#0369a1,#0f172a);color:white;padding:28px;'>
          <div style='font-size:13px;letter-spacing:.08em;color:#bae6fd;'>环境 ＞ 个股 ＞ 情绪 ＞ 技术</div>
          <h1 style='margin:10px 0 4px;font-size:28px;'>今日交易系统执行报告</h1>
          <div>{escape(report.updated_at.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))}</div>
        </div>
        <div style='padding:24px;'>
          <div style='border-left:6px solid {action_color};background:white;border-radius:18px;padding:18px;margin-bottom:18px;'>
            <h2 style='margin:0 0 8px;color:{action_color};'>{escape(strategy.action_title)}</h2>
            <p style='margin:0;'>{escape(strategy.position_hint)}</p>
          </div>
          <div style='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:18px;'>
            <div style='background:white;border-radius:16px;padding:16px;'><b>上涨家数</b><div style='font-size:28px;color:#16a34a'>{market.up_count}</div></div>
            <div style='background:white;border-radius:16px;padding:16px;'><b>下跌家数</b><div style='font-size:28px;color:#dc2626'>{market.down_count}</div></div>
            <div style='background:white;border-radius:16px;padding:16px;'><b>风险等级</b><div style='font-size:24px'>{escape(market.risk_level)}</div></div>
            <div style='background:white;border-radius:16px;padding:16px;'><b>允许买入</b><div style='font-size:24px'>{'是' if market.allow_buy else '否'}</div></div>
          </div>
          <section style='background:white;border-radius:18px;padding:18px;margin-bottom:18px;'><h2>消息面风险</h2><p>{escape(report.news.summary)}</p><h3>重点官方信息源</h3><ul>{official_html}</ul><h3>新闻摘要</h3><ul>{news_html}</ul></section>
          <section style='background:white;border-radius:18px;padding:18px;margin-bottom:18px;'><h2>硬风控提示</h2><ul>{warnings_html}</ul></section>
          <section style='background:white;border-radius:18px;padding:18px;margin-bottom:18px;'><h2>重点股票池</h2><table style='width:100%;border-collapse:collapse;'><thead><tr style='text-align:left;color:#475569'><th style='padding:10px;'>股票</th><th>分数</th><th>因子</th><th>说明</th></tr></thead><tbody>{selector_html}</tbody></table></section>
          <section style='background:white;border-radius:18px;padding:18px;margin-bottom:18px;'><h2>持仓交易信息</h2><ul>{holding_html}</ul></section>
          <section style='background:#ecfeff;border:1px solid #67e8f9;border-radius:18px;padding:18px;'><h2>今日可验证动作</h2><ol>{checklist_html}</ol></section>
        </div>
      </div>
    </div>
    """


def build_daily_report() -> DailyTradingReport:
    market = get_market_status()
    selector = scan_stocks(market)
    strategy = decide_strategy(market, selector)
    news = fetch_official_news()
    holdings = analyze_holdings(market)
    title = f"今日交易提示：{strategy.action_title}"
    report = DailyTradingReport(
        title=title,
        market=market,
        strategy=strategy,
        news=news,
        selector=selector,
        stock_trade_notes=[score_buy_point(signal, market) for signal in selector[:8]],
        holdings=holdings,
        html="",
    )
    report.html = render_report_html(report)
    return report


def push_daily_report() -> dict[str, object]:
    report = build_daily_report()
    response = send_pushplus_report(report.title, report.html)
    return {"title": report.title, "pushplus": response, "report": report.model_dump(mode="json")}
