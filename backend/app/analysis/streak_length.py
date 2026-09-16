"""Streak-length test: do runs of a repeated digit follow the geometric
distribution implied by iid uniform digits?

Under H0 (digits iid uniform over 10 categories), a run of identical
consecutive digits continues to the next position with probability 1/10
regardless of how long it already is (memoryless), so streak lengths
L = 1, 2, 3, ... follow Geometric(p=9/10) on the positive integers:

    P(L = k) = (1/10)^(k-1) * (9/10),  k = 1, 2, 3, ...

Any real dependence that makes runs longer or shorter than this predicts
(e.g. a bias toward repeats, or an artificial "never repeat" filter)
shows up as a bad fit here, distinct from what the digit-frequency or
conditional-probability tests catch.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats as scipy_stats

from app.analysis._runs import run_lengths
from app.analysis._validation import N_DIGITS, validate_digit_array


@dataclass(frozen=True, slots=True)
class StreakLengthResult:
    n_streaks: int
    bin_labels: list[str]  # e.g. ["1", "2", "3", ">=4"]
    observed_counts: np.ndarray
    expected_counts: np.ndarray
    mean_length_observed: float
    mean_length_expected: float
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int


def streak_length_test(digits: np.ndarray, *, max_bin: int = 4) -> StreakLengthResult:
    digits = validate_digit_array(digits)
    if digits.size < 2:
        raise ValueError("digits must have at least 2 observations to form streaks")
    if max_bin < 2:
        raise ValueError("max_bin must be >= 2")

    lengths = run_lengths(digits)
    n_streaks = int(lengths.size)

    p_continue = 1.0 / N_DIGITS
    capped = np.minimum(lengths, max_bin)
    observed = np.bincount(capped, minlength=max_bin + 1)[1 : max_bin + 1]

    k = np.arange(1, max_bin)
    probs = (p_continue**(k - 1)) * (1 - p_continue)
    tail_prob = p_continue**(max_bin - 1)
    expected_probs = np.concatenate([probs, [tail_prob]])
    expected = expected_probs * n_streaks

    if expected.min() < 1:
        raise ValueError(
            f"window too small for max_bin={max_bin}: smallest expected bin "
            f"count is {expected.min():.3f} (< 1); use a larger window or a "
            "smaller max_bin"
        )

    chi2 = scipy_stats.chisquare(observed, f_exp=expected)
    bin_labels = [str(k_) for k_ in range(1, max_bin)] + [f">={max_bin}"]

    return StreakLengthResult(
        n_streaks=n_streaks,
        bin_labels=bin_labels,
        observed_counts=observed,
        expected_counts=expected,
        mean_length_observed=float(lengths.mean()),
        mean_length_expected=1.0 / (1 - p_continue),
        chi2_statistic=float(chi2.statistic),
        p_value=float(chi2.pvalue),
        degrees_of_freedom=max_bin - 1,
    )
