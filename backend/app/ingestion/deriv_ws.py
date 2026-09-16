"""Single multiplexed connection to the Deriv WS API.

One socket carries every symbol's live tick subscription plus all
request/response traffic (active_symbols, ticks_history), matched by
req_id. This keeps ping/reconnect/backoff logic in one place at the cost
of a reconnect briefly interrupting every symbol at once -- accepted
tradeoff, see project review notes.
"""

import asyncio
import itertools
import json
import logging
from collections.abc import Awaitable, Callable

from websockets.asyncio.client import ClientConnection, connect

from app.ingestion.digits import parse_deriv_message

logger = logging.getLogger(__name__)

TickHandler = Callable[[dict], Awaitable[None]]
OnReconnect = Callable[[], Awaitable[None]]


def next_backoff(current: float, *, base: float, maximum: float) -> float:
    """Exponential backoff, no jitter (caller may add jitter if desired)."""
    if current <= 0:
        return base
    return min(current * 2, maximum)


class DerivConnection:
    def __init__(
        self,
        url: str,
        *,
        ping_interval_seconds: float,
        request_timeout_seconds: float,
        reconnect_backoff_base_seconds: float,
        reconnect_backoff_max_seconds: float,
        on_reconnect: OnReconnect | None = None,
    ) -> None:
        self._url = url
        self._ping_interval_seconds = ping_interval_seconds
        self._request_timeout_seconds = request_timeout_seconds
        self._backoff_base = reconnect_backoff_base_seconds
        self._backoff_max = reconnect_backoff_max_seconds
        self._on_reconnect = on_reconnect

        self._ws: ClientConnection | None = None
        self._req_id_counter = itertools.count(1)
        self._pending: dict[int, asyncio.Future] = {}
        self._tick_handlers: dict[str, TickHandler] = {}

        self._connected = asyncio.Event()
        self._closed = False

    async def wait_connected(self) -> None:
        await self._connected.wait()

    async def close(self) -> None:
        self._closed = True
        if self._ws is not None:
            await self._ws.close()

    async def force_reconnect(self) -> None:
        """Used by the staleness watchdog: the socket looks open but a
        subscription has died silently, so tear it down and let the
        reconnect loop rebuild it."""
        if self._ws is not None:
            await self._ws.close()

    async def run(self) -> None:
        backoff = 0.0
        while not self._closed:
            try:
                async with connect(self._url) as ws:
                    self._ws = ws
                    self._connected.set()
                    backoff = 0.0
                    logger.info("deriv ws connected")

                    if self._on_reconnect is not None:
                        await self._on_reconnect()

                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(self._reader(ws))
                        tg.create_task(self._pinger(ws))
            except Exception:
                logger.exception("deriv ws connection error")

            self._connected.clear()
            self._fail_pending()
            if self._closed:
                return
            backoff = next_backoff(
                backoff, base=self._backoff_base, maximum=self._backoff_max
            )
            logger.warning("reconnecting in %.1fs", backoff)
            await asyncio.sleep(backoff)

    def _fail_pending(self) -> None:
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(ConnectionError("deriv ws connection lost"))
        self._pending.clear()

    async def _pinger(self, ws: ClientConnection) -> None:
        while True:
            await asyncio.sleep(self._ping_interval_seconds)
            await ws.send('{"ping": 1}')

    async def _reader(self, ws: ClientConnection) -> None:
        async for raw in ws:
            try:
                msg = parse_deriv_message(raw)
            except ValueError:
                logger.warning("dropped unparseable ws message")
                continue
            await self._dispatch(msg)
        # A graceful remote close ends the `async for` without raising, but
        # _pinger below never exits on its own -- it would otherwise sit in
        # this TaskGroup for up to ping_interval_seconds before its next
        # send() fails. Raise here so the group tears down immediately.
        raise ConnectionError("deriv ws closed")

    async def _dispatch(self, msg: dict) -> None:
        req_id = msg.get("req_id")
        if req_id is not None and req_id in self._pending:
            fut = self._pending.pop(req_id)
            if not fut.done():
                if msg.get("error"):
                    fut.set_exception(DerivAPIError(msg["error"]))
                else:
                    fut.set_result(msg)
            return

        if msg.get("msg_type") == "tick":
            tick = msg["tick"]
            handler = self._tick_handlers.get(tick["symbol"])
            if handler is not None:
                await handler(tick)

    async def send_request(self, request: dict) -> dict:
        if self._ws is None:
            raise ConnectionError("not connected")
        req_id = next(self._req_id_counter)
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[req_id] = fut
        payload = {**request, "req_id": req_id}
        await self._ws.send(json.dumps(payload))
        try:
            return await asyncio.wait_for(fut, self._request_timeout_seconds)
        finally:
            self._pending.pop(req_id, None)

    async def subscribe_ticks(self, symbol: str, handler: TickHandler) -> None:
        self._tick_handlers[symbol] = handler
        await self.send_request({"ticks": symbol, "subscribe": 1})


class DerivAPIError(Exception):
    def __init__(self, error: dict) -> None:
        super().__init__(error.get("message", str(error)))
        self.error = error
