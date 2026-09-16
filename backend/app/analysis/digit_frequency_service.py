import asyncpg

from app.analysis.cache import WindowedStatCache
from app.analysis.digit_frequency import DigitFrequencyResult, digit_frequency_test
from app.analysis.multiple_comparisons import MultipleComparisonResult, correct_p_values
from app.analysis.repository import fetch_recent_digits
from app.db import get_last_epoch


class DigitFrequencyService:
    def __init__(self, pool: asyncpg.Pool, cache: WindowedStatCache | None = None) -> None:
        self._pool = pool
        self._cache = cache if cache is not None else WindowedStatCache()

    async def get(self, symbol: str, window_size: int) -> DigitFrequencyResult:
        """Chi-square digit-frequency test over the last `window_size`
        ticks of `symbol`. Recomputes only if the symbol's latest stored
        epoch has advanced since the last call with this (symbol,
        window_size) -- no rescan of unchanged data."""
        latest_epoch = await get_last_epoch(self._pool, symbol)

        async def compute() -> DigitFrequencyResult:
            digits = await fetch_recent_digits(self._pool, symbol, window_size)
            if digits.size == 0:
                raise ValueError(f"no ticks stored for symbol {symbol!r}")
            return digit_frequency_test(digits)

        return await self._cache.get_or_compute(
            (symbol, window_size), version=latest_epoch, compute=compute
        )

    async def get_many(
        self,
        symbols: list[str],
        window_size: int,
        *,
        method: str = "holm",
        alpha: float = 0.05,
    ) -> tuple[dict[str, DigitFrequencyResult], MultipleComparisonResult]:
        """Per-symbol results plus a multiple-comparison correction across
        them -- required whenever a test runs over many symbols at once."""
        results = {symbol: await self.get(symbol, window_size) for symbol in symbols}
        correction = correct_p_values(
            list(results.keys()),
            [r.p_value for r in results.values()],
            method=method,
            alpha=alpha,
        )
        return results, correction
