// Plain TS mirrors of backend/app/api/schemas.py. Keep these in sync by
// hand -- there are only ~10 shapes and they change rarely.

export interface SymbolInfo {
  symbol: string
  pip_size: string
  decimals: number
}

export interface DigitFrequencyResponse {
  n: number
  observed_counts: number[]
  expected_counts: number[]
  proportions: number[]
  ci_low: number[]
  ci_high: number[]
  chi2_statistic: number
  p_value: number
  degrees_of_freedom: number
}

export interface ACFResponse {
  n: number
  max_lag: number
  lags: number[]
  values: number[]
  ci_low: number[]
  ci_high: number[]
  p_values: number[]
}

export interface MultipleComparisonResponse {
  labels: string[]
  raw_p_values: number[]
  corrected_p_values: number[]
  reject: boolean[]
  method: string
  alpha: number
}

export interface ACFWithCorrectionResponse {
  acf: ACFResponse
  lag_correction: MultipleComparisonResponse
}

export interface ConditionalDigitResponse {
  n_transitions: number
  counts: number[][]
  row_totals: number[]
  conditional_probs: number[][]
  ci_low: number[][]
  ci_high: number[][]
  chi2_statistic: number
  p_value: number
  degrees_of_freedom: number
}

export interface StreakLengthResponse {
  n_streaks: number
  bin_labels: string[]
  observed_counts: number[]
  expected_counts: number[]
  mean_length_observed: number
  mean_length_expected: number
  chi2_statistic: number
  p_value: number
  degrees_of_freedom: number
}

export interface RiseFallResponse {
  n_rises: number
  n_falls: number
  n_ties_dropped: number
  n_runs: number
  expected_runs: number
  z_statistic: number
  p_value: number
}

export interface SummaryResponse<T> {
  results: Record<string, T>
  correction: MultipleComparisonResponse
  skipped: Record<string, string>
}

export type DigitFrequencySummaryResponse = SummaryResponse<DigitFrequencyResponse>
export type ConditionalDigitSummaryResponse = SummaryResponse<ConditionalDigitResponse>
export type StreakLengthSummaryResponse = SummaryResponse<StreakLengthResponse>
export type RiseFallSummaryResponse = SummaryResponse<RiseFallResponse>

export interface LiveTick {
  symbol: string
  epoch: number
  quote: string
  digit: number
}
