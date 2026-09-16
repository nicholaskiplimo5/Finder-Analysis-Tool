import numpy as np
import pytest

from app.analysis.streak_length import streak_length_test


def test_seeded_uniform_iid_matches_geometric_distribution():
    rng = np.random.default_rng(42)
    digits = rng.integers(0, 10, size=60_000)

    result = streak_length_test(digits)

    assert result.p_value > 0.05
    assert result.bin_labels == ["1", "2", "3", ">=4"]
    assert result.observed_counts.sum() == result.n_streaks
    assert abs(result.mean_length_observed - result.mean_length_expected) < 0.02
    assert result.mean_length_expected == pytest.approx(10 / 9)


def test_injected_repeat_bias_is_detected():
    # 30% of the time, force a repeat of the previous digit; otherwise a
    # fresh iid draw. This inflates the run-continuation probability well
    # above the iid baseline of 1/10, producing longer streaks than the
    # geometric null predicts.
    rng = np.random.default_rng(9)
    n = 60_000
    digits = np.empty(n, dtype=np.int64)
    digits[0] = rng.integers(0, 10)
    repeat_prob = 0.3
    for i in range(1, n):
        digits[i] = digits[i - 1] if rng.random() < repeat_prob else rng.integers(0, 10)

    result = streak_length_test(digits)

    assert result.p_value < 0.001
    assert result.mean_length_observed > result.mean_length_expected * 1.3


def test_rejects_too_short_input():
    with pytest.raises(ValueError):
        streak_length_test(np.array([5]))


def test_rejects_max_bin_below_two():
    rng = np.random.default_rng(1)
    digits = rng.integers(0, 10, size=1000)
    with pytest.raises(ValueError):
        streak_length_test(digits, max_bin=1)


def test_rejects_window_too_small_for_max_bin():
    # Tiny sample: the tail bin's expected count collapses well below 1
    # for a reasonable max_bin, and the error should be explicit rather
    # than a silently unreliable chi-square result.
    digits = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
    with pytest.raises(ValueError):
        streak_length_test(digits, max_bin=4)


def test_rejects_out_of_range_digits():
    with pytest.raises(ValueError):
        streak_length_test(np.array([0, 1, 10, 2, 3]))
