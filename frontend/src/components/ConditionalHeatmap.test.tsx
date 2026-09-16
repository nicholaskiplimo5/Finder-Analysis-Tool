import { describe, expect, it } from "vitest"
import type { ConditionalDigitResponse } from "../api/types"
import { buildHeatmapCells } from "./ConditionalHeatmap.transforms"

function makeResponse(): ConditionalDigitResponse {
  const size = 10
  const uniform = 0.1
  return {
    n_transitions: 9999,
    counts: Array.from({ length: size }, () => Array(size).fill(100)),
    row_totals: Array(size).fill(1000),
    conditional_probs: Array.from({ length: size }, (_, i) =>
      Array.from({ length: size }, (_, j) => (i === 7 && j === 3 ? 0.8 : uniform)),
    ),
    ci_low: Array.from({ length: size }, () => Array(size).fill(0.08)),
    ci_high: Array.from({ length: size }, () => Array(size).fill(0.12)),
    chi2_statistic: 500,
    p_value: 0.0,
    degrees_of_freedom: 81,
  }
}

describe("buildHeatmapCells", () => {
  it("flattens the 10x10 matrix into 100 (row, col) cells", () => {
    const cells = buildHeatmapCells(makeResponse())
    expect(cells).toHaveLength(100)
  })

  it("preserves row/col indexing so a cell maps back to the right transition", () => {
    const cells = buildHeatmapCells(makeResponse())
    const cell = cells.find((c) => c.row === 7 && c.col === 3)
    expect(cell).toBeDefined()
    expect(cell!.prob).toBe(0.8)

    const other = cells.find((c) => c.row === 2 && c.col === 5)
    expect(other!.prob).toBe(0.1)
  })
})
