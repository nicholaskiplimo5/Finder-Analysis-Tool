"""Staleness detection, independent of transport connection state.

A WebSocket can report itself as open while its tick subscription has
silently died server-side (trap #3). The only reliable signal is wall-clock
time since the last tick actually arrived for a given symbol, so this
watchdog tracks that per symbol and fires a callback when a symbol goes
quiet for longer than its expected cadence allows.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable

ThresholdFn = Callable[[str], float]
OnStale = Callable[[str], Awaitable[None]]


class StalenessWatchdog:
    def __init__(
        self,
        symbols: list[str],
        *,
        threshold_seconds: ThresholdFn,
        on_stale: OnStale,
        check_interval_seconds: float = 5.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._symbols = list(symbols)
        self._threshold_seconds = threshold_seconds
        self._on_stale = on_stale
        self._check_interval_seconds = check_interval_seconds
        self._clock = clock
        self._last_seen: dict[str, float] = {}

    def mark(self, symbol: str) -> None:
        """Record that a tick was just seen for `symbol`."""
        self._last_seen[symbol] = self._clock()

    def stale_symbols(self, *, now: float | None = None) -> list[str]:
        """Pure check: which symbols have gone quiet past their threshold.

        A symbol with no recorded tick yet (not marked since start or
        resubscribe) is not considered stale — it hasn't had a chance to
        prove itself alive or dead.
        """
        now = self._clock() if now is None else now
        stale = []
        for symbol in self._symbols:
            last = self._last_seen.get(symbol)
            if last is None:
                continue
            if now - last > self._threshold_seconds(symbol):
                stale.append(symbol)
        return stale

    async def check_once(self, *, now: float | None = None) -> list[str]:
        """Run one detection pass, firing `on_stale` for each stale symbol.

        Resets each fired symbol's clock so it isn't re-fired every check
        interval while whatever `on_stale` does (e.g. force a reconnect)
        has a chance to bring it back to life.
        """
        now = self._clock() if now is None else now
        stale = self.stale_symbols(now=now)
        for symbol in stale:
            self._last_seen[symbol] = now
            await self._on_stale(symbol)
        return stale

    async def run(self) -> None:
        while True:
            await asyncio.sleep(self._check_interval_seconds)
            await self.check_once()


def make_threshold_fn(
    expected_interval_seconds: Callable[[str], float],
    *,
    multiplier: float,
    floor_seconds: float,
) -> ThresholdFn:
    def threshold(symbol: str) -> float:
        return max(expected_interval_seconds(symbol) * multiplier, floor_seconds)

    return threshold
