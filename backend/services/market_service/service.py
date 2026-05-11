from __future__ import annotations

from importlib import import_module, util
from random import Random
from typing import Any

from backend.services.market_service.models import MarketStatus

_rng = Random(20260511)


def _akshare_available() -> bool:
    return util.find_spec("akshare") is not None


def _load_market_rows() -> list[dict[str, Any]]:
    """Load A-share snapshot from AkShare when installed, otherwise use demo data."""
    if _akshare_available():
        ak = import_module("akshare")
        try:
            df = ak.stock_zh_a_spot_em()
            rows = df.to_dict("records")
            return [
                {
                    "code": str(row.get("代码", "")),
                    "name": row.get("名称", ""),
                    "change_pct": float(row.get("涨跌幅", 0) or 0),
                }
                for row in rows
            ]
        except Exception:
            pass

    rows: list[dict[str, Any]] = []
    for index in range(5200):
        change = _rng.gauss(0.35, 2.4)
        rows.append(
            {
                "code": f"{index:06d}",
                "name": f"演示股票{index}",
                "change_pct": round(change, 2),
            }
        )
    return rows


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


def get_market_status() -> MarketStatus:
    rows = _load_market_rows()
    up_count = sum(1 for row in rows if row["change_pct"] > 0)
    down_count = sum(1 for row in rows if row["change_pct"] < 0)
    limit_up = sum(1 for row in rows if row["change_pct"] >= 9.8)
    limit_down = sum(1 for row in rows if row["change_pct"] <= -9.8)
    broken_limit_up = max(0, int(limit_up * 0.18) + limit_down // 2)
    broken_limit_rate = round(broken_limit_up / max(limit_up + broken_limit_up, 1), 4)
    market_phase = _phase(up_count, down_count, limit_up, limit_down)
    risk_level = _risk_level(market_phase, down_count, broken_limit_rate)
    allow_buy = risk_level != "high" and down_count < 4000

    if risk_level == "high":
        prompt = "当前市场风险高，执行防守策略：禁止开新仓，优先降低仓位。"
    elif allow_buy:
        prompt = f"当前市场：{market_phase}。禁止追高，适合低吸强势股并控制仓位。"
    else:
        prompt = f"当前市场：{market_phase}。等待情绪确认后再参与。"

    return MarketStatus(
        market_status=market_phase,
        up_count=up_count,
        down_count=down_count,
        limit_up=limit_up,
        limit_down=limit_down,
        broken_limit_up=broken_limit_up,
        broken_limit_rate=broken_limit_rate,
        risk_level=risk_level,
        allow_buy=allow_buy,
        prompt=prompt,
    )
