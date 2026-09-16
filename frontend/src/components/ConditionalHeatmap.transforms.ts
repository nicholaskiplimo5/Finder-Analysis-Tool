import type { ConditionalDigitResponse } from "../api/types"

export interface HeatmapCell {
  row: number
  col: number
  prob: number
  count: number
  ciLow: number
  ciHigh: number
}

export function buildHeatmapCells(data: ConditionalDigitResponse): HeatmapCell[] {
  const cells: HeatmapCell[] = []
  for (let i = 0; i < data.conditional_probs.length; i++) {
    for (let j = 0; j < data.conditional_probs[i].length; j++) {
      cells.push({
        row: i,
        col: j,
        prob: data.conditional_probs[i][j],
        count: data.counts[i][j],
        ciLow: data.ci_low[i][j],
        ciHigh: data.ci_high[i][j],
      })
    }
  }
  return cells
}
