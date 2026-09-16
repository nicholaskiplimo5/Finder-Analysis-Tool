"""Generic recompute-on-change cache for windowed statistics.

Shared across analysis modules: digit frequency now, ACF / conditional
probability / streak tests later. Every one of them keys on the same
question -- "has this symbol's stored data advanced since I last computed
this window?" -- so a stat service calls `get_or_compute` with the
current version marker (e.g. the symbol's latest stored epoch) instead of
each stat reimplementing its own cache.
"""

from collections.abc import Awaitable, Callable, Hashable
from typing import TypeVar

T = TypeVar("T")


class WindowedStatCache:
    def __init__(self) -> None:
        self._entries: dict[Hashable, tuple[object, object]] = {}

    async def get_or_compute(
        self,
        key: Hashable,
        *,
        version: object,
        compute: Callable[[], Awaitable[T]],
    ) -> T:
        cached = self._entries.get(key)
        if cached is not None and cached[0] == version:
            return cached[1]  # type: ignore[return-value]
        result = await compute()
        self._entries[key] = (version, result)
        return result

    def invalidate(self, key: Hashable) -> None:
        self._entries.pop(key, None)
