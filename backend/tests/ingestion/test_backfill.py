from decimal import Decimal

import pytest

from app.ingestion.backfill import _make_tick, _paginated_history
from app.models import SymbolMeta


class FakeConn:
    """Simulates ticks_history semantics: given `end` and `count`, returns
    up to `count` most recent points with epoch <= end (or <= latest)."""

    def __init__(self, all_times: list[int], all_prices: list[float]) -> None:
        self._times = all_times
        self._prices = all_prices
        self.requests: list[dict] = []

    async def send_request(self, request: dict) -> dict:
        self.requests.append(request)
        end = request["end"]
        count = request["count"]
        end_epoch = self._times[-1] if end == "latest" else end
        idx = [i for i, t in enumerate(self._times) if t <= end_epoch]
        idx = idx[-count:]
        times = [self._times[i] for i in idx]
        prices = [Decimal(str(self._prices[i])) for i in idx]
        return {"history": {"times": times, "prices": prices}}


@pytest.mark.asyncio
async def test_paginated_history_stops_at_start_epoch():
    conn = FakeConn(list(range(0, 100)), [1.0] * 100)

    collected = []
    async for page in _paginated_history(
        conn, "R_100", start_epoch=50, page_size=30, max_count=None
    ):
        collected.extend(page)

    epochs = [e for e, _ in collected]
    assert min(epochs) == 51  # exclusive of start_epoch
    assert max(epochs) == 99
    assert len(conn.requests) == 2


@pytest.mark.asyncio
async def test_paginated_history_respects_max_count_budget():
    conn = FakeConn(list(range(0, 1000)), [1.0] * 1000)

    collected = []
    async for page in _paginated_history(
        conn, "R_100", start_epoch=None, page_size=100, max_count=250
    ):
        collected.extend(page)

    assert len(collected) == 250
    assert len(conn.requests) == 3
    assert conn.requests[-1]["count"] == 50  # final page trimmed to remaining budget


@pytest.mark.asyncio
async def test_paginated_history_stops_when_history_exhausted():
    conn = FakeConn(list(range(90, 100)), [1.0] * 10)  # only 10 ticks exist at all

    collected = []
    async for page in _paginated_history(
        conn, "R_100", start_epoch=0, page_size=5000, max_count=None
    ):
        collected.extend(page)

    assert len(collected) == 10
    assert len(conn.requests) == 1


def test_make_tick_uses_symbol_decimals_for_digit():
    meta = SymbolMeta(symbol="R_100", pip_size=Decimal("0.01"), decimals=2)
    tick = _make_tick(meta, epoch=123, quote=Decimal("1234.6"))
    assert tick.digit == 0  # 1234.60 -> last digit 0, not the naive "6"
    assert tick.symbol == "R_100"
    assert tick.epoch == 123
