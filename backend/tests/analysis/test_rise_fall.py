import numpy as np
import pytest

from app.analysis.rise_fall import rise_fall_run_test


def test_seeded_iid_direction_passes_runs_test():
    # Unit +/-1 increments with an iid random sign -- no ties, no
    # momentum, no mean-reversion. Runs test should find nothing.
    rng = np.random.default_rng(42)
    n = 60_000
    directions = rng.choice([-1, 1], size=n)
    quotes = np.cumsum(directions).astype(float) + 1000.0

    result = rise_fall_run_test(quotes)

    assert result.p_value > 0.05
    assert result.n_ties_dropped == 0
    assert result.n_rises + result.n_falls == n - 1  # np.diff drops one point


def test_injected_momentum_is_detected():
    # With probability 0.2, the next direction repeats the previous one
    # (momentum/clustering); otherwise a fresh random sign. This produces
    # fewer runs than a random ordering predicts.
    rng = np.random.default_rng(17)
    n = 60_000
    directions = np.empty(n, dtype=np.int64)
    directions[0] = rng.choice([-1, 1])
    momentum_prob = 0.2
    for i in range(1, n):
        directions[i] = (
            directions[i - 1] if rng.random() < momentum_prob else rng.choice([-1, 1])
        )
    quotes = np.cumsum(directions).astype(float) + 1000.0

    result = rise_fall_run_test(quotes)

    assert result.p_value < 0.001
    assert result.n_runs < result.expected_runs  # clustering -> fewer runs
    assert result.z_statistic < 0


def test_ties_are_dropped_not_treated_as_a_direction():
    quotes = np.array([1.0, 1.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0])
    result = rise_fall_run_test(quotes)
    # First two diffs are 0 (ties); the rest alternate rise/fall.
    assert result.n_ties_dropped == 2
    assert result.n_rises + result.n_falls == 7


def test_rejects_too_short_input():
    with pytest.raises(ValueError):
        rise_fall_run_test(np.array([1.0, 2.0]))


def test_rejects_non_1d_input():
    with pytest.raises(ValueError):
        rise_fall_run_test(np.zeros((10, 2)))


def test_rejects_all_ties():
    with pytest.raises(ValueError):
        rise_fall_run_test(np.array([1.0, 1.0, 1.0, 1.0]))


def test_rejects_all_rises_no_falls():
    with pytest.raises(ValueError):
        rise_fall_run_test(np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
