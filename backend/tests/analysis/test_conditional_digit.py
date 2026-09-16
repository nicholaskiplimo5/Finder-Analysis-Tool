import numpy as np
import pytest

from app.analysis.conditional_digit import conditional_digit_distribution


def test_seeded_uniform_iid_passes_independence_test():
    rng = np.random.default_rng(42)
    digits = rng.integers(0, 10, size=60_000)

    result = conditional_digit_distribution(digits)

    assert result.p_value > 0.01
    assert result.degrees_of_freedom == 81  # (10-1)*(10-1)
    assert result.counts.sum() == result.n_transitions == 59_999
    assert np.allclose(result.row_totals, result.counts.sum(axis=1))
    # every row's conditional distribution should be roughly uniform
    assert np.all(np.abs(result.conditional_probs - 0.1) < 0.03)


def test_injected_digit_to_digit_rule_is_detected():
    # 80% of the time, digit 7 is deterministically followed by digit 3;
    # otherwise a fresh iid draw. An artificial pattern the ACF module
    # would largely miss (little linear correlation in the raw digit
    # value) but this test must catch directly.
    rng = np.random.default_rng(11)
    n = 60_000
    digits = np.empty(n, dtype=np.int64)
    digits[0] = rng.integers(0, 10)
    pattern_prob = 0.8
    for i in range(1, n):
        if digits[i - 1] == 7 and rng.random() < pattern_prob:
            digits[i] = 3
        else:
            digits[i] = rng.integers(0, 10)

    result = conditional_digit_distribution(digits)

    assert result.p_value < 0.001
    # P(d_n=3 | d_n-1=7) should sit near pattern_prob + (1-pattern_prob)/10
    assert result.conditional_probs[7, 3] > 0.7
    assert result.ci_low[7, 3] > 0.7
    # an unaffected row should stay close to uniform
    assert np.all(np.abs(result.conditional_probs[2] - 0.1) < 0.03)


def test_ci_bounds_bracket_point_estimate():
    rng = np.random.default_rng(5)
    digits = rng.integers(0, 10, size=10_000)

    result = conditional_digit_distribution(digits)

    assert np.all(result.ci_low <= result.conditional_probs + 1e-12)
    assert np.all(result.conditional_probs <= result.ci_high + 1e-12)


def test_rejects_too_short_input():
    with pytest.raises(ValueError):
        conditional_digit_distribution(np.array([5]))


def test_rejects_out_of_range_digits():
    with pytest.raises(ValueError):
        conditional_digit_distribution(np.array([0, 1, 10, 2]))


def test_rejects_window_too_small_to_cover_all_digits():
    # Only digits 0-2 ever appear as d_{n-1}; digits 3-9 never do, so no
    # row exists for them -- must fail with a clear error, not scipy's
    # cryptic "zero expected frequency" one.
    digits = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
    with pytest.raises(ValueError):
        conditional_digit_distribution(digits)


def test_rejects_invalid_confidence():
    rng = np.random.default_rng(1)
    digits = rng.integers(0, 10, size=200)
    with pytest.raises(ValueError):
        conditional_digit_distribution(digits, confidence=1.0)
