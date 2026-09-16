"""Conditional digit distribution P(d_n | d_{n-1}) and an independence test.

Builds the 10x10 transition-count matrix over consecutive digits and runs
a chi-square test of independence on it: H0 is that d_n is independent of
d_{n-1}, i.e. every row of the matrix has the same distribution. This
catches dependence structure the ACF module can miss entirely -- e.g. "7
is always followed by 3" produces no meaningful linear autocorrelation of
the raw digit value, but shows up immediately as one wildly non-uniform
row here.

Each cell P(d_n=j | d_{n-1}=i) ships a Wilson confidence interval,
binomial within its row (row total transitions starting from digit i).
"""

from dataclasses import dataclass

import numpy as np
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportion_confint

from app.analysis._validation import N_DIGITS, validate_digit_array


@dataclass(frozen=True, slots=True)
class ConditionalDigitResult:
    n_transitions: int
    counts: np.ndarray  # shape (10, 10): counts[i, j] = #(d_{n-1}=i, d_n=j)
    row_totals: np.ndarray  # shape (10,)
    conditional_probs: np.ndarray  # shape (10, 10): counts[i, j] / row_totals[i]
    ci_low: np.ndarray  # shape (10, 10)
    ci_high: np.ndarray  # shape (10, 10)
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int


def conditional_digit_distribution(
    digits: np.ndarray, *, confidence: float = 0.95
) -> ConditionalDigitResult:
    digits = validate_digit_array(digits)
    if digits.size < 2:
        raise ValueError("digits must have at least 2 observations to form transitions")
    if not (0 < confidence < 1):
        raise ValueError("confidence must be in (0, 1)")

    prev, curr = digits[:-1], digits[1:]
    counts = np.zeros((N_DIGITS, N_DIGITS), dtype=np.int64)
    np.add.at(counts, (prev, curr), 1)

    row_totals = counts.sum(axis=1)
    if np.any(row_totals == 0):
        missing = np.nonzero(row_totals == 0)[0].tolist()
        raise ValueError(
            f"no transitions starting from digit(s) {missing}; window too small "
            "to estimate a full conditional distribution"
        )

    chi2, p_value, dof, _expected = chi2_contingency(counts)

    alpha = 1 - confidence
    ci_low = np.empty_like(counts, dtype=float)
    ci_high = np.empty_like(counts, dtype=float)
    for i in range(N_DIGITS):
        low, high = proportion_confint(counts[i], row_totals[i], alpha=alpha, method="wilson")
        ci_low[i] = low
        ci_high[i] = high

    return ConditionalDigitResult(
        n_transitions=int(prev.size),
        counts=counts,
        row_totals=row_totals,
        conditional_probs=counts / row_totals[:, None],
        ci_low=ci_low,
        ci_high=ci_high,
        chi2_statistic=float(chi2),
        p_value=float(p_value),
        degrees_of_freedom=int(dof),
    )
