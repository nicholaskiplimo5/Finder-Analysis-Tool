"""Digit frequency test: are last-digits uniformly distributed?

Pure function over a numpy array of digits. No I/O, no DB -- callers
(app.analysis.digit_frequency_service) supply the array and own caching.

Ships two things per the project's confidence-interval requirement:
  - a chi-square goodness-of-fit statistic + p-value against the uniform
    null (H0: every digit 0-9 equally likely)
  - a Wilson score confidence interval on each digit's observed
    proportion, for plotting frequency bars with error bars rather than
    bare percentages
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats as scipy_stats
from statsmodels.stats.proportion import proportion_confint

from app.analysis._validation import N_DIGITS, validate_digit_array


@dataclass(frozen=True, slots=True)
class DigitFrequencyResult:
    n: int
    observed_counts: np.ndarray  # shape (10,), int
    expected_counts: np.ndarray  # shape (10,), float, uniform n/10
    proportions: np.ndarray  # shape (10,), float
    ci_low: np.ndarray  # shape (10,), float
    ci_high: np.ndarray  # shape (10,), float
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int


def digit_frequency_test(
    digits: np.ndarray, *, confidence: float = 0.95
) -> DigitFrequencyResult:
    digits = validate_digit_array(digits)
    if not (0 < confidence < 1):
        raise ValueError("confidence must be in (0, 1)")

    n = int(digits.size)
    observed = np.bincount(digits, minlength=N_DIGITS)[:N_DIGITS]
    expected = np.full(N_DIGITS, n / N_DIGITS)

    chi2 = scipy_stats.chisquare(observed, f_exp=expected)

    alpha = 1 - confidence
    ci_low, ci_high = proportion_confint(observed, n, alpha=alpha, method="wilson")

    return DigitFrequencyResult(
        n=n,
        observed_counts=observed,
        expected_counts=expected,
        proportions=observed / n,
        ci_low=np.asarray(ci_low, dtype=float),
        ci_high=np.asarray(ci_high, dtype=float),
        chi2_statistic=float(chi2.statistic),
        p_value=float(chi2.pvalue),
        degrees_of_freedom=N_DIGITS - 1,
    )
