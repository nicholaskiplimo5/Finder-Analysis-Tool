"""Canned dataclass results + fake services for API route tests.

These don't re-verify the statistics themselves (that's tests/analysis/,
against real synthetic data) -- they exist so route tests can check
wiring, validation, response shape, and error mapping without a real DB.
"""

import numpy as np

from app.analysis.acf import ACFResult
from app.analysis.conditional_digit import ConditionalDigitResult
from app.analysis.digit_frequency import DigitFrequencyResult
from app.analysis.multiple_comparisons import correct_p_values
from app.analysis.rise_fall import RiseFallRunResult
from app.analysis.streak_length import StreakLengthResult


def make_digit_frequency_result() -> DigitFrequencyResult:
    return DigitFrequencyResult(
        n=1000,
        observed_counts=np.array([100] * 10),
        expected_counts=np.array([100.0] * 10),
        proportions=np.array([0.1] * 10),
        ci_low=np.array([0.08] * 10),
        ci_high=np.array([0.12] * 10),
        chi2_statistic=0.0,
        p_value=1.0,
        degrees_of_freedom=9,
    )


def make_acf_result(max_lag: int = 5) -> ACFResult:
    return ACFResult(
        n=1000,
        max_lag=max_lag,
        lags=np.arange(1, max_lag + 1),
        values=np.zeros(max_lag),
        ci_low=np.full(max_lag, -0.05),
        ci_high=np.full(max_lag, 0.05),
        p_values=np.full(max_lag, 1.0),
    )


def make_conditional_digit_result() -> ConditionalDigitResult:
    counts = np.full((10, 10), 10, dtype=np.int64)
    row_totals = counts.sum(axis=1)
    return ConditionalDigitResult(
        n_transitions=999,
        counts=counts,
        row_totals=row_totals,
        conditional_probs=counts / row_totals[:, None],
        ci_low=np.full((10, 10), 0.05),
        ci_high=np.full((10, 10), 0.15),
        chi2_statistic=0.0,
        p_value=1.0,
        degrees_of_freedom=81,
    )


def make_streak_length_result() -> StreakLengthResult:
    return StreakLengthResult(
        n_streaks=900,
        bin_labels=["1", "2", "3", ">=4"],
        observed_counts=np.array([810, 81, 8, 1]),
        expected_counts=np.array([810.0, 81.0, 8.1, 0.9]),
        mean_length_observed=1.11,
        mean_length_expected=1.111,
        chi2_statistic=0.0,
        p_value=1.0,
        degrees_of_freedom=3,
    )


def make_rise_fall_result() -> RiseFallRunResult:
    return RiseFallRunResult(
        n_rises=500,
        n_falls=499,
        n_ties_dropped=0,
        n_runs=500,
        expected_runs=500.0,
        z_statistic=0.0,
        p_value=1.0,
    )


def _fake_get_many(result, symbols, skipped_symbols, *, method="holm", alpha=0.05):
    """Shared get_many behavior for the fakes below: mirrors the real
    services' partial-tolerance contract (skip symbols that have no
    data, raise if none are left) without hitting a DB."""
    results = {s: result for s in symbols if s not in skipped_symbols}
    skipped = {s: "no ticks stored (fake)" for s in symbols if s in skipped_symbols}
    if not results:
        raise ValueError(f"no configured symbol has enough data yet: {skipped}")
    correction = correct_p_values(
        list(results.keys()), [r.p_value for r in results.values()], method=method, alpha=alpha
    )
    return results, correction, skipped


class FakeDigitFrequencyService:
    def __init__(self, result=None, raise_error: Exception | None = None, skipped_symbols=()):
        self._result = result if result is not None else make_digit_frequency_result()
        self._raise_error = raise_error
        self._skipped_symbols = set(skipped_symbols)

    async def get(self, symbol, window):
        if self._raise_error is not None:
            raise self._raise_error
        return self._result

    async def get_many(self, symbols, window, *, method="holm", alpha=0.05):
        if self._raise_error is not None:
            raise self._raise_error
        return _fake_get_many(self._result, symbols, self._skipped_symbols, method=method, alpha=alpha)


class FakeACFService:
    def __init__(self, max_lag: int = 5, raise_error: Exception | None = None):
        self._result = make_acf_result(max_lag=max_lag)
        self._raise_error = raise_error

    async def get_with_lag_correction(self, symbol, window, max_lag, *, method="holm", alpha=0.05):
        if self._raise_error is not None:
            raise self._raise_error
        result = make_acf_result(max_lag=max_lag)
        correction = correct_p_values(
            [f"lag_{k}" for k in result.lags], result.p_values, method=method, alpha=alpha
        )
        return result, correction


class FakeConditionalDigitService:
    def __init__(self, result=None, raise_error: Exception | None = None, skipped_symbols=()):
        self._result = result if result is not None else make_conditional_digit_result()
        self._raise_error = raise_error
        self._skipped_symbols = set(skipped_symbols)

    async def get(self, symbol, window):
        if self._raise_error is not None:
            raise self._raise_error
        return self._result

    async def get_many(self, symbols, window, *, method="holm", alpha=0.05):
        if self._raise_error is not None:
            raise self._raise_error
        return _fake_get_many(self._result, symbols, self._skipped_symbols, method=method, alpha=alpha)


class FakeStreakLengthService:
    def __init__(self, result=None, raise_error: Exception | None = None, skipped_symbols=()):
        self._result = result if result is not None else make_streak_length_result()
        self._raise_error = raise_error
        self._skipped_symbols = set(skipped_symbols)

    async def get(self, symbol, window, *, max_bin=4):
        if self._raise_error is not None:
            raise self._raise_error
        return self._result

    async def get_many(self, symbols, window, *, method="holm", alpha=0.05):
        if self._raise_error is not None:
            raise self._raise_error
        return _fake_get_many(self._result, symbols, self._skipped_symbols, method=method, alpha=alpha)


class FakeRiseFallService:
    def __init__(self, result=None, raise_error: Exception | None = None, skipped_symbols=()):
        self._result = result if result is not None else make_rise_fall_result()
        self._raise_error = raise_error
        self._skipped_symbols = set(skipped_symbols)

    async def get(self, symbol, window):
        if self._raise_error is not None:
            raise self._raise_error
        return self._result

    async def get_many(self, symbols, window, *, method="holm", alpha=0.05):
        if self._raise_error is not None:
            raise self._raise_error
        return _fake_get_many(self._result, symbols, self._skipped_symbols, method=method, alpha=alpha)


__all__ = [
    "FakeACFService",
    "FakeConditionalDigitService",
    "FakeDigitFrequencyService",
    "FakeRiseFallService",
    "FakeStreakLengthService",
    "make_acf_result",
    "make_conditional_digit_result",
    "make_digit_frequency_result",
    "make_rise_fall_result",
    "make_streak_length_result",
]
