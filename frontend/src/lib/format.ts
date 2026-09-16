export function formatPercent(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`
}

export function formatPValue(p: number): string {
  if (p < 0.0001) return "p < 0.0001"
  return `p = ${p.toFixed(4)}`
}

export function formatCompact(value: number): string {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value)
}
