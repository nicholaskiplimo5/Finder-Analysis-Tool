import { describe, expect, it } from "vitest"
import type { StreakLengthResponse } from "../api/types"
import { buildStreakRows } from "./StreakComparisonChart.transforms"

function makeResponse(): StreakLengthResponse {
  return {
    n_streaks: 900,
    bin_labels: ["1", "2", "3", ">=4"],
    observed_counts: [810, 81, 8, 1],
    expected_counts: [810.0, 81.0, 8.1, 0.9],
    mean_length_observed: 1.11,
    mean_length_expected: 1.111,
    chi2_statistic: 0.05,
    p_value: 0.9,
    degrees_of_freedom: 3,
  }
}

describe("buildStreakRows", () => {
  it("pairs each bin label with its observed and expected counts in order", () => {
    const rows = buildStreakRows(makeResponse())
    expect(rows).toEqual([
      { bin: "1", observed: 810, expected: 810.0 },
      { bin: "2", observed: 81, expected: 81.0 },
      { bin: "3", observed: 8, expected: 8.1 },
      { bin: ">=4", observed: 1, expected: 0.9 },
    ])
  })
})
