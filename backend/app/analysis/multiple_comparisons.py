"""Multiple-comparison correction for a batch of p-values.

Any statistic run across many symbols (or, later, many lags) inflates the
chance of at least one false "pattern found" purely from running enough
tests. Default is Holm-Bonferroni: controls the family-wise error rate
(appropriate here, since a false positive would be reported as evidence
of an exploitable pattern) and is uniformly more powerful than plain
Bonferroni.
"""

from dataclasses import dataclass

import numpy as np
from statsmodels.stats.multitest import multipletests


@dataclass(frozen=True, slots=True)
class MultipleComparisonResult:
    labels: list[str]
    raw_p_values: np.ndarray
    corrected_p_values: np.ndarray
    reject: np.ndarray
    method: str
    alpha: float


def correct_p_values(
    labels: list[str],
    p_values: list[float] | np.ndarray,
    *,
    method: str = "holm",
    alpha: float = 0.05,
) -> MultipleComparisonResult:
    if len(labels) != len(p_values):
        raise ValueError("labels and p_values must be the same length")
    if len(labels) == 0:
        raise ValueError("p_values must be non-empty")

    reject, corrected, _, _ = multipletests(p_values, alpha=alpha, method=method)

    return MultipleComparisonResult(
        labels=list(labels),
        raw_p_values=np.asarray(p_values, dtype=float),
        corrected_p_values=np.asarray(corrected, dtype=float),
        reject=np.asarray(reject, dtype=bool),
        method=method,
        alpha=alpha,
    )
