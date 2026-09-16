import numpy as np
import pytest

from app.analysis.digit_frequency import N_DIGITS, digit_frequency_test


def test_seeded_uniform_rng_passes_chi_square():
    # A true uniform digit stream (what Deriv's CSPRNG should produce)
    # must not be flagged as patterned.
    rng = np.random.default_rng(42)
    digits = rng.integers(0, 10, size=100_000)

    result = digit_frequency_test(digits)

    assert result.p_value > 0.01
    assert result.n == 100_000
    assert result.observed_counts.sum() == 100_000
    assert np.allclose(result.expected_counts, 10_000.0)
    assert result.degrees_of_freedom == N_DIGITS - 1


def test_injected_bias_is_detected():
    # Digit 7 twice as likely as the rest -- an artificial pattern the
    # test must catch.
    rng = np.random.default_rng(7)
    probs = np.full(10, 1 / 11)
    probs[7] = 2 / 11
    digits = rng.choice(10, size=50_000, p=probs)

    result = digit_frequency_test(digits)

    assert result.p_value < 0.01
    assert result.observed_counts[7] > result.expected_counts[7]


def test_confidence_intervals_bracket_true_uniform_proportion_for_most_digits():
    rng = np.random.default_rng(123)
    digits = rng.integers(0, 10, size=200_000)

    result = digit_frequency_test(digits)

    true_p = 0.1
    contains = (result.ci_low <= true_p) & (true_p <= result.ci_high)
    # 95% CIs shouldn't all miss; allow some slack for sampling variance
    # rather than pinning the exact count, which would be seed-fragile.
    assert contains.sum() >= 7


def test_ci_bounds_are_ordered_and_within_unit_interval():
    rng = np.random.default_rng(5)
    digits = rng.integers(0, 10, size=10_000)

    result = digit_frequency_test(digits)

    assert np.all(result.ci_low <= result.proportions)
    assert np.all(result.proportions <= result.ci_high)
    assert np.all(result.ci_low >= 0.0)
    assert np.all(result.ci_high <= 1.0)


def test_rejects_out_of_range_digits():
    with pytest.raises(ValueError):
        digit_frequency_test(np.array([0, 1, 10]))


def test_rejects_negative_digits():
    with pytest.raises(ValueError):
        digit_frequency_test(np.array([0, -1, 5]))


def test_rejects_empty_input():
    with pytest.raises(ValueError):
        digit_frequency_test(np.array([], dtype=np.int64))


def test_rejects_non_1d_input():
    with pytest.raises(ValueError):
        digit_frequency_test(np.zeros((10, 2), dtype=np.int64))


def test_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        digit_frequency_test(np.array([1, 2, 3]), confidence=1.0)
