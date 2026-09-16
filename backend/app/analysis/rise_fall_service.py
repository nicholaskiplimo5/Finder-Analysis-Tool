import asyncpg

from app.analysis.cache import WindowedStatCache
from app.analysis.multiple_comparisons import MultipleComparisonResult, correct_p_values
from app.analysis.repository import fetch_recent_quotes
from app.analysis.rise_fall import RiseFallRunResult, rise_fall_run_test
from app.db import get_last_epoch


class RiseFallService:
    def __init__(self, pool: asyncpg.Pool, cache: WindowedStatCache | None = None) -> None:
        self._pool = pool
        self._cache = cache if cache is not None else WindowedStatCache()

    async def get(self, symbol: str, window_size: int) -> RiseFallRunResult:
        """Rise/fall run test over the last `window_size` quotes of
        `symbol`. Recomputes only if the symbol's latest stored epoch has
        advanced since the last call."""
        latest_epoch = await get_last_epoch(self._pool, symbol)

        async def compute() -> RiseFallRunResult:
            quotes = await fetch_recent_quotes(self._pool, symbol, window_size)
            if quotes.size == 0:
                raise ValueError(f"no ticks stored for symbol {symbol!r}")
            return rise_fall_run_test(quotes)

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
    ) -> tuple[dict[str, RiseFallRunResult], MultipleComparisonResult]:
        """Per-symbol rise/fall run test plus a multiple-comparison
        correction across symbols."""
        results = {symbol: await self.get(symbol, window_size) for symbol in symbols}
        correction = correct_p_values(
            list(results.keys()),
            [r.p_value for r in results.values()],
            method=method,
            alpha=alpha,
        )
        return results, correction
