import type { ACFWithCorrectionResponse } from "../api/types"

export interface ACFRow {
  lag: number
  value: number
  ciLow: number
  ciHigh: number
  bandWidth: number
  pValue: number
  correctedPValue: number
  reject: boolean
}

export function buildACFRows(data: ACFWithCorrectionResponse): ACFRow[] {
  return data.acf.lags.map((lag, i) => ({
    lag,
    value: data.acf.values[i],
    ciLow: data.acf.ci_low[i],
    ciHigh: data.acf.ci_high[i],
    bandWidth: data.acf.ci_high[i] - data.acf.ci_low[i],
    pValue: data.acf.p_values[i],
    correctedPValue: data.lag_correction.corrected_p_values[i],
    reject: data.lag_correction.reject[i],
  }))
}
