from __future__ import annotations

from backend.services.market_service.models import MarketStatus, StockSnapshot


def _phase(up_count: int, down_count: int, limit_up: int, limit_down: int) -> str:
    total = max(up_count + down_count, 1)
    up_ratio = up_count / total
    if down_count >= 4000 or limit_down > limit_up * 1.5:
        return "退潮"
    if up_ratio >= 0.7 and limit_up >= 70:
        return "强修复"
    if up_ratio >= 0.55:
        return "弱修复"
    if up_ratio >= 0.45:
        return "震荡"
    return "分歧"


def _risk_level(phase: str, down_count: int, broken_limit_rate: float) -> str:
    if down_count >= 4000 or broken_limit_rate >= 0.45 or phase == "退潮":
        return "high"
    if broken_limit_rate >= 0.25 or phase in {"分歧", "震荡"}:
        return "medium"
    return "low"


def analyze_market(snapshots: list[StockSnapshot]) -> MarketStatus:
    up_count = sum(1 for row in snapshots if row.change_pct > 0)
    down_count = sum(1 for row in snapshots if row.change_pct < 0)
    flat_count = len(snapshots) - up_count - down_count
    limit_up = sum(1 for row in snapshots if row.change_pct >= 9.8)
    limit_down = sum(1 for row in snapshots if row.change_pct <= -9.8)

    # AkShare spot snapshots do not provide intraday opened-limit history directly.
    # MVP estimates broken boards from large-amplitude strong stocks that failed to close at limit-up.
    broken_limit_up = sum(
        1
        for row in snapshots
        if row.change_pct < 9.8 and row.change_pct >= 5 and row.amplitude >= 8
    )
    broken_limit_rate = round(broken_limit_up / max(limit_up + broken_limit_up, 1), 4)
    market_phase = _phase(up_count, down_count, limit_up, limit_down)
    risk_level = _risk_level(market_phase, down_count, broken_limit_rate)
    allow_buy = risk_level != "high" and down_count < 4000

    if risk_level == "high":
        prompt = "当前市场风险高：禁止开新仓，优先防守，等待亏钱效应释放。"
    elif risk_level == "medium":
        prompt = f"当前市场：{market_phase}。仅允许轻仓低吸强势股，禁止追高。"
    else:
        prompt = f"当前市场：{market_phase}。可小仓试错，仍需严格止损。"

    return MarketStatus(
        market_status=market_phase,
        up_count=up_count,
        down_count=down_count,
        flat_count=flat_count,
        limit_up=limit_up,
        limit_down=limit_down,
        broken_limit_up=broken_limit_up,
        broken_limit_rate=broken_limit_rate,
        risk_level=risk_level,
        allow_buy=allow_buy,
        prompt=prompt,
    )
