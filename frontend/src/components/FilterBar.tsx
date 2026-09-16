import type { SymbolInfo } from "../api/types"

const WINDOW_PRESETS = [1000, 2000, 5000, 10000, 20000]
const MAX_LAG_PRESETS = [10, 20, 30, 50]
const MAX_BIN_PRESETS = [3, 4, 5, 6]

interface FilterBarProps {
  symbols: SymbolInfo[]
  symbol: string
  onSymbolChange: (symbol: string) => void
  windowSize: number
  onWindowSizeChange: (size: number) => void
  maxLag: number
  onMaxLagChange: (n: number) => void
  maxBin: number
  onMaxBinChange: (n: number) => void
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
      {label}
      {children}
    </label>
  )
}

const selectClass = "rounded-md border px-2 py-1 text-sm"
const selectStyle = {
  borderColor: "var(--border-ring)",
  color: "var(--text-primary)",
  backgroundColor: "var(--surface-1)",
}

/**
 * One row, above every chart it scopes (dataviz skill: filters are
 * never per-chart). Symbol and window scope every stat; max-lag and
 * max-bin are parameters of one statistic's own definition (ACF, streak
 * length) rather than a data slice, but still live here rather than
 * inside their chart cards, to keep a single consistent control row.
 */
export function FilterBar({
  symbols,
  symbol,
  onSymbolChange,
  windowSize,
  onWindowSizeChange,
  maxLag,
  onMaxLagChange,
  maxBin,
  onMaxBinChange,
}: FilterBarProps) {
  return (
    <div
      className="flex flex-wrap items-center gap-4 rounded-lg border p-3"
      style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)" }}
    >
      <Field label="Symbol">
        <select
          value={symbol}
          onChange={(e) => onSymbolChange(e.target.value)}
          className={selectClass}
          style={selectStyle}
        >
          {symbols.length === 0 && <option value="">no symbols yet</option>}
          {symbols.map((s) => (
            <option key={s.symbol} value={s.symbol}>
              {s.symbol}
            </option>
          ))}
        </select>
      </Field>

      <Field label="Window">
        <select
          value={windowSize}
          onChange={(e) => onWindowSizeChange(Number(e.target.value))}
          className={selectClass}
          style={selectStyle}
        >
          {WINDOW_PRESETS.map((size) => (
            <option key={size} value={size}>
              {size.toLocaleString()} ticks
            </option>
          ))}
        </select>
      </Field>

      <Field label="ACF lags">
        <select
          value={maxLag}
          onChange={(e) => onMaxLagChange(Number(e.target.value))}
          className={selectClass}
          style={selectStyle}
        >
          {MAX_LAG_PRESETS.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </Field>

      <Field label="Streak bins">
        <select
          value={maxBin}
          onChange={(e) => onMaxBinChange(Number(e.target.value))}
          className={selectClass}
          style={selectStyle}
        >
          {MAX_BIN_PRESETS.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </Field>
    </div>
  )
}
