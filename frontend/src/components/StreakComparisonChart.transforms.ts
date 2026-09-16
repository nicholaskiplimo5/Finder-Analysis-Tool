import type { StreakLengthResponse } from "../api/types"

export interface StreakRow {
  bin: string
  observed: number
  expected: number
}

export function buildStreakRows(data: StreakLengthResponse): StreakRow[] {
  return data.bin_labels.map((bin, i) => ({
    bin,
    observed: data.observed_counts[i],
    expected: data.expected_counts[i],
  }))
}
