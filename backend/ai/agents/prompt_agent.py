from __future__ import annotations

from backend.services.crawler_service.models import CrawledItem
from backend.services.decision_service.models import StrategyDecision
from backend.services.deepseek_service.models import AIAnalysis
from backend.services.market_service.models import MarketStatus
from backend.services.risk_service.service import risk_tip
from backend.services.selector_service.models import StockSignal


def build_ai_prompt(
    market: MarketStatus,
    signals: list[StockSignal],
    ai_analysis: AIAnalysis,
    decision: StrategyDecision,
    crawled_items: list[CrawledItem],
) -> dict[str, object]:
    """Build final AI-style diagnosis after DeepSeek analysis and strategy decision."""
    leader_text = "暂无高分候选，等待下一小时扫描"
    if signals:
        top = signals[0]
        leader_text = f"最高分：{top.name}({top.stock})，{top.score}分，命中：{'、'.join(top.factors)}"

    crawl_text = "；".join(item.title for item in crawled_items[:3]) or "无外部爬取数据"
    message = (
        f"当前市场：{market.market_status}\n"
        f"系统风控：{risk_tip(market)}\n"
        f"DeepSeek诊断：{ai_analysis.summary}\n"
        f"DeepSeek风险分：{ai_analysis.risk_score}/100，情绪：{ai_analysis.sentiment}\n"
        f"爬取摘要：{crawl_text}\n"
        f"策略决策：{decision.action}，仓位：{decision.position}，"
        f"{'允许开仓' if decision.allow_buy else '禁止开仓'}\n"
        f"选股诊断：{leader_text}"
    )
    return {
        "market_status": market.market_status,
        "risk_level": market.risk_level,
        "allow_buy": decision.allow_buy,
        "message": message,
        "deepseek": ai_analysis.to_dict(),
        "decision": decision.to_dict(),
        "crawled_items": [item.to_dict() for item in crawled_items[:10]],
        "top_signals": [signal.to_dict() for signal in signals[:5]],
    }
