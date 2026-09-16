"""Response models: plain JSON-serializable mirrors of the analysis
dataclasses (which hold numpy arrays, not JSON-serializable as-is)."""

from pydantic import BaseModel

from app.analysis.acf import ACFResult
from app.analysis.conditional_digit import ConditionalDigitResult
from app.analysis.digit_frequency import DigitFrequencyResult
from app.analysis.multiple_comparisons import MultipleComparisonResult
from app.analysis.rise_fall import RiseFallRunResult
from app.analysis.streak_length import StreakLengthResult


class DigitFrequencyResponse(BaseModel):
    n: int
    observed_counts: list[int]
    expected_counts: list[float]
    proportions: list[float]
    ci_low: list[float]
    ci_high: list[float]
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int

    @classmethod
    def from_result(cls, r: DigitFrequencyResult) -> "DigitFrequencyResponse":
        return cls(
            n=r.n,
            observed_counts=r.observed_counts.tolist(),
            expected_counts=r.expected_counts.tolist(),
            proportions=r.proportions.tolist(),
            ci_low=r.ci_low.tolist(),
            ci_high=r.ci_high.tolist(),
            chi2_statistic=r.chi2_statistic,
            p_value=r.p_value,
            degrees_of_freedom=r.degrees_of_freedom,
        )


class ACFResponse(BaseModel):
    n: int
    max_lag: int
    lags: list[int]
    values: list[float]
    ci_low: list[float]
    ci_high: list[float]
    p_values: list[float]

    @classmethod
    def from_result(cls, r: ACFResult) -> "ACFResponse":
        return cls(
            n=r.n,
            max_lag=r.max_lag,
            lags=r.lags.tolist(),
            values=r.values.tolist(),
            ci_low=r.ci_low.tolist(),
            ci_high=r.ci_high.tolist(),
            p_values=r.p_values.tolist(),
        )


class ConditionalDigitResponse(BaseModel):
    n_transitions: int
    counts: list[list[int]]
    row_totals: list[int]
    conditional_probs: list[list[float]]
    ci_low: list[list[float]]
    ci_high: list[list[float]]
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int

    @classmethod
    def from_result(cls, r: ConditionalDigitResult) -> "ConditionalDigitResponse":
        return cls(
            n_transitions=r.n_transitions,
            counts=r.counts.tolist(),
            row_totals=r.row_totals.tolist(),
            conditional_probs=r.conditional_probs.tolist(),
            ci_low=r.ci_low.tolist(),
            ci_high=r.ci_high.tolist(),
            chi2_statistic=r.chi2_statistic,
            p_value=r.p_value,
            degrees_of_freedom=r.degrees_of_freedom,
        )


class StreakLengthResponse(BaseModel):
    n_streaks: int
    bin_labels: list[str]
    observed_counts: list[int]
    expected_counts: list[float]
    mean_length_observed: float
    mean_length_expected: float
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int

    @classmethod
    def from_result(cls, r: StreakLengthResult) -> "StreakLengthResponse":
        return cls(
            n_streaks=r.n_streaks,
            bin_labels=r.bin_labels,
            observed_counts=r.observed_counts.tolist(),
            expected_counts=r.expected_counts.tolist(),
            mean_length_observed=r.mean_length_observed,
            mean_length_expected=r.mean_length_expected,
            chi2_statistic=r.chi2_statistic,
            p_value=r.p_value,
            degrees_of_freedom=r.degrees_of_freedom,
        )


class RiseFallResponse(BaseModel):
    n_rises: int
    n_falls: int
    n_ties_dropped: int
    n_runs: int
    expected_runs: float
    z_statistic: float
    p_value: float

    @classmethod
    def from_result(cls, r: RiseFallRunResult) -> "RiseFallResponse":
        return cls(
            n_rises=r.n_rises,
            n_falls=r.n_falls,
            n_ties_dropped=r.n_ties_dropped,
            n_runs=r.n_runs,
            expected_runs=r.expected_runs,
            z_statistic=r.z_statistic,
            p_value=r.p_value,
        )


class MultipleComparisonResponse(BaseModel):
    labels: list[str]
    raw_p_values: list[float]
    corrected_p_values: list[float]
    reject: list[bool]
    method: str
    alpha: float

    @classmethod
    def from_result(cls, r: MultipleComparisonResult) -> "MultipleComparisonResponse":
        return cls(
            labels=r.labels,
            raw_p_values=r.raw_p_values.tolist(),
            corrected_p_values=r.corrected_p_values.tolist(),
            reject=r.reject.tolist(),
            method=r.method,
            alpha=r.alpha,
        )


class ACFWithCorrectionResponse(BaseModel):
    acf: ACFResponse
    lag_correction: MultipleComparisonResponse


class DigitFrequencySummaryResponse(BaseModel):
    results: dict[str, DigitFrequencyResponse]
    correction: MultipleComparisonResponse
    # Symbol -> reason, for a configured symbol with too little data yet
    # (e.g. still mid cold-start backfill) rather than failing the whole
    # summary over one symbol not being ready.
    skipped: dict[str, str]


class ConditionalDigitSummaryResponse(BaseModel):
    results: dict[str, ConditionalDigitResponse]
    correction: MultipleComparisonResponse
    skipped: dict[str, str]


class StreakLengthSummaryResponse(BaseModel):
    results: dict[str, StreakLengthResponse]
    correction: MultipleComparisonResponse
    skipped: dict[str, str]


class RiseFallSummaryResponse(BaseModel):
    results: dict[str, RiseFallResponse]
    correction: MultipleComparisonResponse
    skipped: dict[str, str]


class SymbolInfo(BaseModel):
    symbol: str
    pip_size: str
    decimals: int
