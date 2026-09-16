import numpy as np
import pytest

from app.analysis.multiple_comparisons import correct_p_values


def test_holm_correction_matches_hand_computed_example():
    # Holm step-down on p=[0.01, 0.02, 0.03] with alpha=0.05:
    # thresholds are 0.05/3, 0.05/2, 0.05/1 -- all three clear their
    # threshold, so all reject; adjusted p-values are the cumulative max
    # of (n - i + 1) * p_(i) in sorted order, mapped back to input order.
    result = correct_p_values(["a", "b", "c"], [0.01, 0.02, 0.03], method="holm")

    assert np.allclose(result.corrected_p_values, [0.03, 0.04, 0.04])
    assert list(result.reject) == [True, True, True]
    assert result.labels == ["a", "b", "c"]


def test_corrected_p_values_never_smaller_than_raw():
    raw = [0.001, 0.2, 0.5, 0.03]
    result = correct_p_values(["a", "b", "c", "d"], raw, method="holm")

    assert np.all(result.corrected_p_values >= np.array(raw) - 1e-12)


def test_holm_controls_family_wise_rate_under_many_true_nulls():
    # 100 independent true-null p-values (uniform under H0). Naive
    # per-test alpha=0.05 rejects ~5% of them by chance; Holm should
    # reject far fewer for a batch this size where no real effect exists.
    rng = np.random.default_rng(0)
    raw = rng.uniform(size=100)
    labels = [str(i) for i in range(100)]

    naive_rejections = int((raw < 0.05).sum())
    result = correct_p_values(labels, raw, method="holm", alpha=0.05)

    assert naive_rejections > 0  # sanity: the naive comparison isn't vacuous
    assert int(result.reject.sum()) < naive_rejections


def test_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        correct_p_values(["a", "b"], [0.1])


def test_rejects_empty_input():
    with pytest.raises(ValueError):
        correct_p_values([], [])
