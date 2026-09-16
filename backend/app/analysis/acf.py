"""Autocorrelation of the digit stream, with confidence bands and a
per-lag significance test.

Digits are categorical, but the sample ACF of the raw digit value is a
standard diagnostic for iid-ness: under a true uniform iid stream
Cov(d_n, d_{n+k}) = 0 for every k > 0, so any lag whose |r_k| clears its
confidence band is evidence of linear serial dependence. This is a
complement to, not a replacement for, the conditional-probability matrix
(module 2 next step), which can catch non-linear dependence ACF would
miss entirely.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats as scipy_stats
from statsmodels.tsa.stattools import acf as _sm_acf


@dataclass(frozen=True, slots=True)
class ACFResult:
    n: int
    max_lag: int
    lags: np.ndarray  # 1..max_lag
    values: np.ndarray  # r_k for k=1..max_lag (lag 0, always 1, is excluded)
    ci_low: np.ndarray
    ci_high: np.ndarray
    p_values: np.ndarray  # per-lag two-sided p-value, H0: rho_k = 0


def acf_with_confidence_bands(
    x: np.ndarray, *, max_lag: int, alpha: float = 0.05
) -> ACFResult:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("x must be a 1-D array")
    if x.size < 2:
        raise ValueError("x must have at least 2 observations")
    if max_lag < 1:
        raise ValueError("max_lag must be >= 1")
    if max_lag >= x.size:
        raise ValueError("max_lag must be smaller than the number of observations")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0, 1)")

    values_with_lag0, confint = _sm_acf(
        x,
        nlags=max_lag,
        alpha=alpha,
        fft=True,
        bartlett_confint=True,
        result_object=False,
    )

    values = values_with_lag0[1:]
    confint = confint[1:]  # drop the lag-0 row, which is always [1, 1]
    ci_low = confint[:, 0]
    ci_high = confint[:, 1]

    # The confidence band's half-width implies the standard error Bartlett's
    # formula used for this lag; reuse it for a p-value consistent with the
    # plotted band, rather than assuming a lag-independent se = 1/sqrt(n).
    z_crit = scipy_stats.norm.ppf(1 - alpha / 2)
    se = (ci_high - values) / z_crit
    z = values / se
    p_values = 2 * (1 - scipy_stats.norm.cdf(np.abs(z)))

    return ACFResult(
        n=int(x.size),
        max_lag=max_lag,
        lags=np.arange(1, max_lag + 1),
        values=values,
        ci_low=ci_low,
        ci_high=ci_high,
        p_values=p_values,
    )
