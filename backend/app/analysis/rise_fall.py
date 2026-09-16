"""Rise/fall run test: does the sequence of up/down tick movements show
runs consistent with a random ordering?

This is the classical Wald-Wolfowitz runs test applied to tick
direction. Given n1 rises and n2 falls arranged in some order, under H0
(the order is random, i.e. no momentum and no mean-reversion pattern) the
number of runs R has a known mean and variance, so R is compared to that
via a normal approximation.

Ties (quote_n == quote_n-1) carry no rise/fall direction and are dropped
before counting runs, per the classical two-sample runs test. This is
Rise/Fall's own contract dimension, distinct from the digit-level tests
(frequency, ACF, conditional distribution, streaks) elsewhere in this
module -- it operates on the quote sequence, not the last digit.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats as scipy_stats

from app.analysis._runs import run_lengths


@dataclass(frozen=True, slots=True)
class RiseFallRunResult:
    n_rises: int
    n_falls: int
    n_ties_dropped: int
    n_runs: int
    expected_runs: float
    z_statistic: float
    p_value: float


def rise_fall_run_test(quotes: np.ndarray) -> RiseFallRunResult:
    quotes = np.asarray(quotes, dtype=float)
    if quotes.ndim != 1:
        raise ValueError("quotes must be a 1-D array")
    if quotes.size < 3:
        raise ValueError("quotes must have at least 3 observations to test runs")

    diffs = np.diff(quotes)
    direction = np.sign(diffs)
    n_ties = int(np.sum(direction == 0))
    direction = direction[direction != 0]

    n1 = int(np.sum(direction == 1))  # rises
    n2 = int(np.sum(direction == -1))  # falls
    if n1 == 0 or n2 == 0:
        raise ValueError(
            "need at least one rise and one fall (after dropping ties) to run the test"
        )

    n_runs = int(run_lengths(direction).size)
    n = n1 + n2

    expected_runs = (2 * n1 * n2) / n + 1
    variance = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n**2 * (n - 1))
    if variance <= 0:
        raise ValueError("degenerate input: zero variance for the runs statistic")

    z = (n_runs - expected_runs) / np.sqrt(variance)
    p_value = float(2 * (1 - scipy_stats.norm.cdf(abs(z))))

    return RiseFallRunResult(
        n_rises=n1,
        n_falls=n2,
        n_ties_dropped=n_ties,
        n_runs=n_runs,
        expected_runs=float(expected_runs),
        z_statistic=float(z),
        p_value=p_value,
    )
