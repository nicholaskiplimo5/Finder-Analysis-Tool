import numpy as np
import pytest

from app.analysis.acf import acf_with_confidence_bands


def test_seeded_uniform_iid_shows_mostly_non_significant_lags():
    rng = np.random.default_rng(42)
    digits = rng.integers(0, 10, size=50_000).astype(float)

    result = acf_with_confidence_bands(digits, max_lag=20)

    assert result.lags.tolist() == list(range(1, 21))
    assert result.values.shape == (20,)
    # A true iid stream will still throw the occasional lag past alpha=0.05
    # by chance (~1 in 20); assert the overwhelming majority clear it
    # rather than demanding all 20 do, which would be seed-fragile.
    assert (result.p_values > 0.05).sum() >= 15
    assert np.all(result.ci_low <= result.values)
    assert np.all(result.values <= result.ci_high)


def test_injected_lag1_dependence_is_detected():
    # With probability 0.3, d_n copies d_{n-1}; otherwise a fresh iid draw.
    # That construction has a known, non-zero Cov(d_n, d_{n-1}), an
    # artificial pattern the ACF must catch at lag 1 (and, by chained
    # copying, weakly at lag 2-3 too).
    rng = np.random.default_rng(3)
    n = 50_000
    digits = np.empty(n)
    digits[0] = rng.integers(0, 10)
    copy_prob = 0.3
    copy_mask = rng.random(n - 1) < copy_prob
    fresh = rng.integers(0, 10, size=n - 1)
    for i in range(1, n):
        digits[i] = digits[i - 1] if copy_mask[i - 1] else fresh[i - 1]

    result = acf_with_confidence_bands(digits, max_lag=5)

    assert result.values[0] > 0.2  # lag 1: strong positive correlation
    assert result.p_values[0] < 0.001


def test_rejects_non_1d_input():
    with pytest.raises(ValueError):
        acf_with_confidence_bands(np.zeros((10, 2)), max_lag=1)


def test_rejects_too_short_input():
    with pytest.raises(ValueError):
        acf_with_confidence_bands(np.array([1.0]), max_lag=1)


def test_rejects_max_lag_below_one():
    with pytest.raises(ValueError):
        acf_with_confidence_bands(np.arange(10, dtype=float), max_lag=0)


def test_rejects_max_lag_at_or_above_n():
    with pytest.raises(ValueError):
        acf_with_confidence_bands(np.arange(10, dtype=float), max_lag=10)


def test_rejects_invalid_alpha():
    with pytest.raises(ValueError):
        acf_with_confidence_bands(np.arange(10, dtype=float), max_lag=2, alpha=0.0)
