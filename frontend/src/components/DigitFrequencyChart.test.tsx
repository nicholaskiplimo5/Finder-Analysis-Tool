import { describe, expect, it } from "vitest"
import type { DigitFrequencyResponse } from "../api/types"
import { buildDigitFrequencyRows } from "./DigitFrequencyChart.transforms"

function makeResponse(overrides: Partial<DigitFrequencyResponse> = {}): DigitFrequencyResponse {
  return {
    n: 1000,
    observed_counts: [120, 90, 100, 100, 100, 100, 100, 100, 100, 90],
    expected_counts: Array(10).fill(100),
    proportions: [0.12, 0.09, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.09],
    ci_low: Array(10).fill(0.08),
    ci_high: Array(10).fill(0.12),
    chi2_statistic: 5.0,
    p_value: 0.5,
    degrees_of_freedom: 9,
    ...overrides,
  }
}

describe("buildDigitFrequencyRows", () => {
  it("produces one row per digit with the right fields", () => {
    const rows = buildDigitFrequencyRows(makeResponse())
    expect(rows).toHaveLength(10)
    expect(rows[0].digit).toBe(0)
    expect(rows[0].observed).toBe(120)
    expect(rows[0].expected).toBe(100)
    expect(rows[0].proportion).toBe(0.12)
  })

  it("converts the proportion CI into count-scale asymmetric error bars", () => {
    const data = makeResponse({
      observed_counts: [120, ...Array(9).fill(100)],
      ci_low: [0.1, ...Array(9).fill(0.08)],
      ci_high: [0.13, ...Array(9).fill(0.12)],
      n: 1000,
    })
    const rows = buildDigitFrequencyRows(data)
    // ci_low=0.10 -> 100 count; ci_high=0.13 -> 130 count; observed=120
    expect(rows[0].errorY[0]).toBeCloseTo(20) // 120 - 100
    expect(rows[0].errorY[1]).toBeCloseTo(10) // 130 - 120
  })

  it("never returns a negative error bar even if observed sits outside its own CI due to rounding", () => {
    const data = makeResponse({
      observed_counts: [100, ...Array(9).fill(100)],
      ci_low: [0.11, ...Array(9).fill(0.08)], // ci_low above observed proportion
      ci_high: [0.12, ...Array(9).fill(0.12)],
    })
    const rows = buildDigitFrequencyRows(data)
    expect(rows[0].errorY[0]).toBeGreaterThanOrEqual(0)
  })
})
