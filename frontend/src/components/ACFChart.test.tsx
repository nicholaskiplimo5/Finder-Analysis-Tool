import { describe, expect, it } from "vitest"
import type { ACFWithCorrectionResponse } from "../api/types"
import { buildACFRows } from "./ACFChart.transforms"

function makeResponse(): ACFWithCorrectionResponse {
  return {
    acf: {
      n: 5000,
      max_lag: 3,
      lags: [1, 2, 3],
      values: [0.02, -0.01, 0.15],
      ci_low: [-0.03, -0.03, 0.1],
      ci_high: [0.03, 0.03, 0.2],
      p_values: [0.4, 0.7, 0.0001],
    },
    lag_correction: {
      labels: ["lag_1", "lag_2", "lag_3"],
      raw_p_values: [0.4, 0.7, 0.0001],
      corrected_p_values: [0.7, 0.7, 0.0003],
      reject: [false, false, true],
      method: "holm",
      alpha: 0.05,
    },
  }
}

describe("buildACFRows", () => {
  it("zips acf values with their lag-correction counterparts by index", () => {
    const rows = buildACFRows(makeResponse())
    expect(rows).toHaveLength(3)
    expect(rows[2].lag).toBe(3)
    expect(rows[2].value).toBe(0.15)
    expect(rows[2].pValue).toBe(0.0001)
    expect(rows[2].correctedPValue).toBe(0.0003)
    expect(rows[2].reject).toBe(true)
  })

  it("computes the band width from ci_high - ci_low for the area overlay", () => {
    const rows = buildACFRows(makeResponse())
    expect(rows[0].bandWidth).toBeCloseTo(0.06)
    expect(rows[2].bandWidth).toBeCloseTo(0.1)
  })
})
