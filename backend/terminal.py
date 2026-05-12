from __future__ import annotations

import json
from shutil import get_terminal_size
from textwrap import shorten

from backend.services.crawler_service.models import CrawledItem
from backend.services.decision_service.models import StrategyDecision
from backend.services.deepseek_service.models import AIAnalysis
from backend.services.market_service.models import MarketStatus
from backend.services.selector_service.models import StockSignal


def line(char: str = "─") -> str:
    return char * min(get_terminal_size((120, 20)).columns, 120)


def badge(value: str) -> str:
    return f"【{value}】"


def render_market(market: MarketStatus, *, data_source: str) -> str:
    allow = "允许开仓" if market.allow_buy else "禁止开仓"
    rows = [
        line("═"),
        f"AI 情绪交易系统 | 1小时策略扫描 | 数据源: {data_source}",
        line("─"),
        f"市场状态 {badge(market.market_status)}  风险 {badge(market.risk_level)}  操作 {badge(allow)}",
        f"上涨 {market.up_count:>5} | 下跌 {market.down_count:>5} | 平盘 {market.flat_count:>4} | "
        f"涨停 {market.limit_up:>3} | 跌停 {market.limit_down:>3} | 炸板率 {market.broken_limit_rate * 100:>5.1f}%",
        f"提示：{market.prompt}",
        line("═"),
    ]
    return "\n".join(rows)


def render_crawled_items(items: list[CrawledItem]) -> str:
    output = ["爬取数据", line("─")]
    if not items:
        output.append("暂无爬取数据。")
        return "\n".join(output)
    for index, item in enumerate(items[:8], start=1):
        output.append(
            f"{index:>2}. [{item.source}] {shorten(item.title, width=70, placeholder='…')}"
        )
        if item.summary:
            output.append(f"    {shorten(item.summary, width=100, placeholder='…')}")
    return "\n".join(output)


def render_signals(signals: list[StockSignal]) -> str:
    if not signals:
        return "\nAI 选股池：暂无符合条件候选。\n"

    headers = ("排名", "代码", "名称", "评分", "命中因子", "解释")
    widths = (4, 8, 12, 7, 30, 46)
    fmt = "  ".join(f"{{:<{width}}}" for width in widths)
    output = ["AI 选股池 TOP", line("─"), fmt.format(*headers), line("─")]
    for index, signal in enumerate(signals, start=1):
        output.append(
            fmt.format(
                index,
                signal.stock,
                shorten(signal.name, width=widths[2], placeholder="…"),
                f"{signal.score:.1f}",
                shorten("、".join(signal.factors), width=widths[4], placeholder="…"),
                shorten(signal.explanation, width=widths[5], placeholder="…"),
            )
        )
    output.append(line("─"))
    return "\n".join(output)


def render_deepseek(ai: AIAnalysis) -> str:
    rows = [
        "DeepSeek AI 分析",
        line("─"),
        f"提供方：{ai.provider} | 模型：{ai.model} | 情绪：{ai.sentiment} | 风险分：{ai.risk_score}/100 | 建议：{ai.suggested_action}",
        f"摘要：{ai.summary}",
    ]
    for point in ai.key_points[:6]:
        rows.append(f"- {point}")
    return "\n".join(rows)


def render_decision(decision: StrategyDecision) -> str:
    rows = [
        "策略最终决策",
        line("─"),
        f"动作：{badge(decision.action)}  仓位：{badge(decision.position)}  {'允许开仓' if decision.allow_buy else '禁止开仓'}",
    ]
    for reason in decision.reasons:
        rows.append(f"- {reason}")
    rows.append(line("═"))
    return "\n".join(rows)


def render_ai(ai_payload: dict[str, object]) -> str:
    return "\n".join(["AI 综合通知文案", line("─"), str(ai_payload["message"]), line("═")])


def render_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
