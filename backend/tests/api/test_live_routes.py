import json
from decimal import Decimal

import pytest

from app.api.routes import live as live_routes
from app.models import Tick
from tests.api.conftest import make_test_app
from tests.api.settings_helper import make_settings


class FakeRequest:
    """`is_disconnected()` returns False `disconnect_after` times, then
    True -- lets a test drive the poll loop for a fixed number of
    iterations without a real HTTP connection."""

    def __init__(self, disconnect_after: int) -> None:
        self._calls = 0
        self._disconnect_after = disconnect_after

    async def is_disconnected(self) -> bool:
        self._calls += 1
        return self._calls > self._disconnect_after


@pytest.mark.asyncio
async def test_event_stream_yields_new_ticks_and_advances_epoch(monkeypatch):
    async def fake_get_last_epoch(pool, symbol):
        return 100

    calls = {"n": 0}

    async def fake_fetch_ticks_since(pool, symbol, since_epoch, limit=1000):
        calls["n"] += 1
        if calls["n"] == 1:
            assert since_epoch == 100
            return [Tick(symbol=symbol, epoch=101, quote=Decimal("1234.56"), digit=6)]
        return []

    monkeypatch.setattr(live_routes, "get_last_epoch", fake_get_last_epoch)
    monkeypatch.setattr(live_routes, "fetch_ticks_since", fake_fetch_ticks_since)

    request = FakeRequest(disconnect_after=2)
    events = [
        e
        async for e in live_routes._event_stream(
            request, pool=object(), symbol="R_100", poll_interval=0.0
        )
    ]

    assert len(events) == 1
    payload = json.loads(events[0].removeprefix("data: ").strip())
    assert payload == {"symbol": "R_100", "epoch": 101, "quote": "1234.56", "digit": 6}


@pytest.mark.asyncio
async def test_event_stream_starts_from_negative_one_when_no_data_yet(monkeypatch):
    async def fake_get_last_epoch(pool, symbol):
        return None

    seen_since_epoch = []

    async def fake_fetch_ticks_since(pool, symbol, since_epoch, limit=1000):
        seen_since_epoch.append(since_epoch)
        return []

    monkeypatch.setattr(live_routes, "get_last_epoch", fake_get_last_epoch)
    monkeypatch.setattr(live_routes, "fetch_ticks_since", fake_fetch_ticks_since)

    request = FakeRequest(disconnect_after=1)
    events = [
        e
        async for e in live_routes._event_stream(
            request, pool=object(), symbol="R_100", poll_interval=0.0
        )
    ]

    assert events == []
    assert seen_since_epoch == [-1]


@pytest.mark.asyncio
async def test_event_stream_stops_on_disconnect_without_polling_again(monkeypatch):
    async def fake_get_last_epoch(pool, symbol):
        return 0

    calls = {"n": 0}

    async def fake_fetch_ticks_since(pool, symbol, since_epoch, limit=1000):
        calls["n"] += 1
        return []

    monkeypatch.setattr(live_routes, "get_last_epoch", fake_get_last_epoch)
    monkeypatch.setattr(live_routes, "fetch_ticks_since", fake_fetch_ticks_since)

    request = FakeRequest(disconnect_after=0)  # disconnected from the first check
    events = [
        e
        async for e in live_routes._event_stream(
            request, pool=object(), symbol="R_100", poll_interval=0.0
        )
    ]

    assert events == []
    assert calls["n"] == 0


def test_live_ticks_unknown_symbol_404():
    client = make_test_app(
        live_routes.router,
        pool=object(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/live-ticks/NOPE")
    assert resp.status_code == 404
