import asyncpg

from app.analysis.acf import ACFResult, acf_with_confidence_bands
from app.analysis.cache import WindowedStatCache
from app.analysis.multiple_comparisons import MultipleComparisonResult, correct_p_values
from app.analysis.repository import fetch_recent_digits
from app.db import get_last_epoch


class ACFService:
    def __init__(self, pool: asyncpg.Pool, cache: WindowedStatCache | None = None) -> None:
        self._pool = pool
        self._cache = cache if cache is not None else WindowedStatCache()

    async def get(
        self, symbol: str, window_size: int, max_lag: int, *, alpha: float = 0.05
    ) -> ACFResult:
        """ACF over the last `window_size` digits of `symbol`, up to
        `max_lag`. Recomputes only if the symbol's latest stored epoch
        has advanced since the last call with these parameters."""
        latest_epoch = await get_last_epoch(self._pool, symbol)

        async def compute() -> ACFResult:
            digits = await fetch_recent_digits(self._pool, symbol, window_size)
            if digits.size == 0:
                raise ValueError(f"no ticks stored for symbol {symbol!r}")
            return acf_with_confidence_bands(digits, max_lag=max_lag, alpha=alpha)

        return await self._cache.get_or_compute(
            (symbol, window_size, max_lag, alpha),
            version=latest_epoch,
            compute=compute,
        )

    async def get_with_lag_correction(
        self,
        symbol: str,
        window_size: int,
        max_lag: int,
        *,
        method: str = "holm",
        alpha: float = 0.05,
    ) -> tuple[ACFResult, MultipleComparisonResult]:
        """Same as `get`, plus a multiple-comparison correction across the
        per-lag p-values -- required since testing many lags at once
        inflates the chance of a spurious "significant" one."""
        result = await self.get(symbol, window_size, max_lag, alpha=alpha)
        correction = correct_p_values(
            [f"lag_{k}" for k in result.lags],
            result.p_values,
            method=method,
            alpha=alpha,
        )
        return result, correction
