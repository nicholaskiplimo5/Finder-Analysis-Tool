import type { DigitFrequencyResponse } from "../api/types"

export interface DigitFrequencyRow {
  digit: number
  observed: number
  expected: number
  proportion: number
  ciLow: number
  ciHigh: number
  errorY: [number, number]
}

export function buildDigitFrequencyRows(data: DigitFrequencyResponse): DigitFrequencyRow[] {
  return data.observed_counts.map((observed, i) => {
    const ciLowCount = data.ci_low[i] * data.n
    const ciHighCount = data.ci_high[i] * data.n
    return {
      digit: i,
      observed,
      expected: data.expected_counts[i],
      proportion: data.proportions[i],
      ciLow: data.ci_low[i],
      ciHigh: data.ci_high[i],
      errorY: [Math.max(0, observed - ciLowCount), Math.max(0, ciHighCount - observed)],
    }
  })
}
