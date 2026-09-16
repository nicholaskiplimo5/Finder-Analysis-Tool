import asyncio

import pytest

from app.ingestion.deriv_ws import DerivAPIError, DerivConnection, next_backoff


class FakeWS:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, payload: str) -> None:
        self.sent.append(payload)


def make_conn() -> DerivConnection:
    return DerivConnection(
        "wss://fake",
        ping_interval_seconds=25.0,
        request_timeout_seconds=1.0,
        reconnect_backoff_base_seconds=1.0,
        reconnect_backoff_max_seconds=60.0,
    )


@pytest.mark.asyncio
async def test_send_request_resolves_future_on_matching_req_id():
    conn = make_conn()
    conn._ws = FakeWS()

    async def deliver_response():
        await asyncio.sleep(0)  # let send_request register req_id=1 first
        await conn._dispatch(
            {"req_id": 1, "msg_type": "active_symbols", "active_symbols": []}
        )

    responder = asyncio.create_task(deliver_response())
    result = await conn.send_request({"active_symbols": "brief"})
    await responder

    assert result["msg_type"] == "active_symbols"


@pytest.mark.asyncio
async def test_send_request_raises_deriv_api_error_on_error_response():
    conn = make_conn()
    conn._ws = FakeWS()

    async def deliver_error():
        await asyncio.sleep(0)
        await conn._dispatch(
            {"req_id": 1, "error": {"code": "InvalidSymbol", "message": "bad symbol"}}
        )

    responder = asyncio.create_task(deliver_error())
    with pytest.raises(DerivAPIError):
        await conn.send_request({"ticks_history": "NOPE"})
    await responder


@pytest.mark.asyncio
async def test_send_request_times_out_if_no_response():
    conn = make_conn()
    conn._ws = FakeWS()
    with pytest.raises(TimeoutError):
        await conn.send_request({"ping": 1})


@pytest.mark.asyncio
async def test_tick_dispatch_routes_to_registered_handler():
    conn = make_conn()
    received = []

    async def handler(tick):
        received.append(tick)

    conn._tick_handlers["R_100"] = handler
    await conn._dispatch(
        {"msg_type": "tick", "tick": {"symbol": "R_100", "epoch": 1, "quote": "1.23"}}
    )

    assert len(received) == 1
    assert received[0]["symbol"] == "R_100"


@pytest.mark.asyncio
async def test_tick_dispatch_ignores_symbol_with_no_handler():
    conn = make_conn()
    # Should not raise even though nothing is subscribed for this symbol.
    await conn._dispatch(
        {"msg_type": "tick", "tick": {"symbol": "R_999", "epoch": 1, "quote": "1"}}
    )


def test_next_backoff_doubles_until_capped():
    assert next_backoff(0, base=1.0, maximum=60.0) == 1.0
    assert next_backoff(1.0, base=1.0, maximum=60.0) == 2.0
    assert next_backoff(2.0, base=1.0, maximum=60.0) == 4.0
    assert next_backoff(32.0, base=1.0, maximum=60.0) == 60.0  # 64 capped to 60
    assert next_backoff(60.0, base=1.0, maximum=60.0) == 60.0
