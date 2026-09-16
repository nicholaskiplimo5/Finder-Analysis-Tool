import { formatPValue } from "../lib/format"

interface PValueBadgeProps {
  pValue: number
  alpha?: number
  correctedPValue?: number
  correctionMethod?: string
}

/**
 * Deliberately neutral: no red/green "significant!" coloring. This is a
 * measurement tool for a CSPRNG-driven stream, not a trading terminal --
 * a colored alarm badge would read as a buy/sell signal, which is
 * exactly what this project must never imply. The number and the
 * threshold are stated in text; the reader draws their own conclusion.
 */
export function PValueBadge({ pValue, alpha = 0.05, correctedPValue, correctionMethod }: PValueBadgeProps) {
  const belowAlpha = pValue < alpha

  return (
    <span
      className="inline-flex flex-wrap items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
      style={{ borderColor: "var(--border-ring)", color: "var(--text-primary)" }}
    >
      <span style={{ color: "var(--text-secondary)" }}>{formatPValue(pValue)}</span>
      {correctedPValue !== undefined && (
        <span className="tabular-nums" style={{ color: "var(--text-muted)" }}>
          ({correctionMethod ?? "corrected"}: {formatPValue(correctedPValue)})
        </span>
      )}
      <span style={{ color: "var(--text-muted)" }}>{belowAlpha ? `below α=${alpha}` : `above α=${alpha}`}</span>
    </span>
  )
}
