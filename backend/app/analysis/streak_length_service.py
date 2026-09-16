import asyncpg

from app.analysis.cache import WindowedStatCache
from app.analysis.multiple_comparisons import MultipleComparisonResult, correct_p_values
from app.analysis.repository import fetch_recent_digits
from app.analysis.streak_length import StreakLengthResult, streak_length_test
from app.db import get_last_epoch


class StreakLengthService:
    def __init__(self, pool: asyncpg.Pool, cache: WindowedStatCache | None = None) -> None:
        self._pool = pool
        self._cache = cache if cache is not None else WindowedStatCache()

    async def get(
        self, symbol: str, window_size: int, *, max_bin: int = 4
    ) -> StreakLengthResult:
        """Streak-length-vs-geometric test over the last `window_size`
        digits of `symbol`. Recomputes only if the symbol's latest stored
        epoch has advanced since the last call."""
        latest_epoch = await get_last_epoch(self._pool, symbol)

        async def compute() -> StreakLengthResult:
            digits = await fetch_recent_digits(self._pool, symbol, window_size)
            if digits.size == 0:
                raise ValueError(f"no ticks stored for symbol {symbol!r}")
            return streak_length_test(digits, max_bin=max_bin)

        return await self._cache.get_or_compute(
            (symbol, window_size, max_bin), version=latest_epoch, compute=compute
        )

    async def get_many(
        self,
        symbols: list[str],
        window_size: int,
        *,
        method: str = "holm",
        alpha: float = 0.05,
    ) -> tuple[dict[str, StreakLengthResult], MultipleComparisonResult]:
        """Per-symbol streak-length test plus a multiple-comparison
        correction across symbols."""
        results = {symbol: await self.get(symbol, window_size) for symbol in symbols}
        correction = correct_p_values(
            list(results.keys()),
            [r.p_value for r in results.values()],
            method=method,
            alpha=alpha,
        )
        return results, correction
