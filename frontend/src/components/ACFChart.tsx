import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { TooltipContentProps } from "recharts"
import type { ACFWithCorrectionResponse } from "../api/types"
import { formatPValue } from "../lib/format"
import type { ACFRow } from "./ACFChart.transforms"
import { buildACFRows } from "./ACFChart.transforms"
import { ChartCard } from "./ChartCard"

function ACFTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload as ACFRow
  return (
    <div
      className="rounded-md border px-3 py-2 text-sm shadow-sm"
      style={{ backgroundColor: "var(--surface-1)", borderColor: "var(--border-ring)", color: "var(--text-primary)" }}
    >
      <div className="font-semibold">Lag {row.lag}</div>
      <div style={{ color: "var(--text-secondary)" }}>
        r ={" "}
        <span className="tabular-nums font-medium" style={{ color: "var(--text-primary)" }}>
          {row.value.toFixed(4)}
        </span>{" "}
        (95% CI {row.ciLow.toFixed(4)} to {row.ciHigh.toFixed(4)})
      </div>
      <div style={{ color: "var(--text-secondary)" }}>{formatPValue(row.pValue)} (raw)</div>
      <div style={{ color: "var(--text-secondary)" }}>{formatPValue(row.correctedPValue)} (Holm-corrected)</div>
    </div>
  )
}

function ACFTable({ rows }: { rows: ACFRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: "var(--text-secondary)" }}>
            <th className="px-2 py-1 text-left font-medium">Lag</th>
            <th className="px-2 py-1 text-right font-medium">r</th>
            <th className="px-2 py-1 text-right font-medium">95% CI</th>
            <th className="px-2 py-1 text-right font-medium">p (raw)</th>
            <th className="px-2 py-1 text-right font-medium">p (Holm)</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {rows.map((row) => (
            <tr key={row.lag} style={{ borderTop: "1px solid var(--gridline)" }}>
              <td className="px-2 py-1">{row.lag}</td>
              <td className="px-2 py-1 text-right">{row.value.toFixed(4)}</td>
              <td className="px-2 py-1 text-right">
                {row.ciLow.toFixed(4)} to {row.ciHigh.toFixed(4)}
              </td>
              <td className="px-2 py-1 text-right">{row.pValue.toFixed(4)}</td>
              <td className="px-2 py-1 text-right">{row.correctedPValue.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface ACFChartProps {
  data: ACFWithCorrectionResponse
  isFetching?: boolean
}

export function ACFChart({ data, isFetching }: ACFChartProps) {
  const rows = buildACFRows(data)

  return (
    <ChartCard
      title="Autocorrelation (ACF)"
      isFetching={isFetching}
      caption={`Sample autocorrelation of the digit stream, n=${data.acf.n.toLocaleString()}, lags 1-${data.acf.max_lag}. Band = 95% confidence (Bartlett's formula). p-values are Holm-corrected across all ${data.acf.max_lag} lags shown -- correcting for testing many lags at once.`}
      chart={
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={rows} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
            <CartesianGrid stroke="var(--gridline)" vertical={false} />
            <XAxis
              dataKey="lag"
              tick={{ fill: "var(--text-muted)", fontSize: 12 }}
              axisLine={{ stroke: "var(--baseline)" }}
              tickLine={false}
              label={{ value: "lag", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 11 }}
            />
            <YAxis
              tick={{ fill: "var(--text-muted)", fontSize: 12 }}
              axisLine={{ stroke: "var(--baseline)" }}
              tickLine={false}
              width={48}
            />
            <ReferenceLine y={0} stroke="var(--baseline)" />
            <Tooltip content={ACFTooltip} />
            <Area dataKey="ciLow" stackId="band" stroke="none" fill="transparent" isAnimationActive={false} />
            <Area
              dataKey="bandWidth"
              stackId="band"
              stroke="none"
              fill="var(--series-1)"
              fillOpacity={0.1}
              isAnimationActive={false}
            />
            <Line
              dataKey="value"
              stroke="var(--series-1)"
              strokeWidth={2}
              dot={{ r: 4, fill: "var(--series-1)", stroke: "var(--surface-1)", strokeWidth: 2 }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      }
      table={<ACFTable rows={rows} />}
    />
  )
}
