from __future__ import annotations

from importlib import import_module, util
from random import Random
from typing import Any

from backend.services.market_service.models import StockSnapshot

_rng = Random(20260511)


class MarketDataProvider:
    """A-share snapshot provider with AkShare first and deterministic demo fallback."""

    def __init__(self, force_demo: bool = False) -> None:
        self.force_demo = force_demo
        self.last_source = "demo"
        self.last_error = ""

    def load_snapshots(self) -> list[StockSnapshot]:
        if not self.force_demo and util.find_spec("akshare") is not None:
            try:
                snapshots = self._load_from_akshare()
                if snapshots:
                    self.last_source = "akshare.stock_zh_a_spot_em"
                    self.last_error = ""
                    return snapshots
            except Exception as exc:  # AkShare/network errors should not break local MVP scans.
                self.last_error = f"AkShare failed, fallback to demo data: {exc}"

        self.last_source = "demo"
        return self._load_demo_snapshots()

    def _load_from_akshare(self) -> list[StockSnapshot]:
        ak = import_module("akshare")
        df = ak.stock_zh_a_spot_em()
        return [self._row_to_snapshot(row) for row in df.to_dict("records")]

    @staticmethod
    def _float(row: dict[str, Any], key: str) -> float:
        value = row.get(key, 0)
        if value in (None, "", "-"):
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _row_to_snapshot(self, row: dict[str, Any]) -> StockSnapshot:
        return StockSnapshot(
            code=str(row.get("代码", "")),
            name=str(row.get("名称", "")),
            change_pct=self._float(row, "涨跌幅"),
            price=self._float(row, "最新价"),
            high=self._float(row, "最高"),
            low=self._float(row, "最低"),
            open_price=self._float(row, "今开"),
            volume=self._float(row, "成交量"),
            amount=self._float(row, "成交额"),
            amplitude=self._float(row, "振幅"),
            turnover=self._float(row, "换手率"),
        )

    def _load_demo_snapshots(self) -> list[StockSnapshot]:
        snapshots: list[StockSnapshot] = []
        names = ["平安银行", "贵州茅台", "比亚迪", "宁德时代", "中信证券", "东方财富"]
        for index in range(5200):
            change = _rng.gauss(0.3, 2.5)
            if index % 173 == 0:
                change = 10.0
            if index % 389 == 0:
                change = -10.0
            price = round(max(2.0, _rng.uniform(4, 80)), 2)
            snapshots.append(
                StockSnapshot(
                    code=f"{index:06d}",
                    name=names[index % len(names)] if index < len(names) else f"演示股票{index}",
                    change_pct=round(change, 2),
                    price=price,
                    high=round(price * (1 + abs(_rng.gauss(0.015, 0.015))), 2),
                    low=round(price * (1 - abs(_rng.gauss(0.012, 0.01))), 2),
                    open_price=round(price * (1 - change / 100), 2),
                    volume=round(_rng.uniform(20_000, 2_000_000), 2),
                    amount=round(_rng.uniform(20_000_000, 2_000_000_000), 2),
                    amplitude=round(abs(_rng.gauss(4, 2)), 2),
                    turnover=round(abs(_rng.gauss(4, 3)), 2),
                )
            )
        return snapshots
