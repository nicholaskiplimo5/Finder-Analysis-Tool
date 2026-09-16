import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { TooltipContentProps } from "recharts"
import type { StreakLengthResponse } from "../api/types"
import { ChartCard } from "./ChartCard"
import { PValueBadge } from "./PValueBadge"
import type { StreakRow } from "./StreakComparisonChart.transforms"
import { buildStreakRows } from "./StreakComparisonChart.transforms"

function StreakTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload as StreakRow
  return (
    <div
      className="rounded-md border px-3 py-2 text-sm shadow-sm"
      style={{ backgroundColor: "var(--surface-1)", borderColor: "var(--border-ring)", color: "var(--text-primary)" }}
    >
      <div className="font-semibold">Streak length {row.bin}</div>
      <div style={{ color: "var(--text-secondary)" }}>
        Observed:{" "}
        <span className="tabular-nums font-medium" style={{ color: "var(--text-primary)" }}>
          {row.observed.toLocaleString()}
        </span>
      </div>
      <div style={{ color: "var(--text-secondary)" }}>
        Expected (Geometric): <span className="tabular-nums">{row.expected.toFixed(1)}</span>
      </div>
    </div>
  )
}

function StreakTable({ rows }: { rows: StreakRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: "var(--text-secondary)" }}>
            <th className="px-2 py-1 text-left font-medium">Streak length</th>
            <th className="px-2 py-1 text-right font-medium">Observed</th>
            <th className="px-2 py-1 text-right font-medium">Expected</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {rows.map((row) => (
            <tr key={row.bin} style={{ borderTop: "1px solid var(--gridline)" }}>
              <td className="px-2 py-1">{row.bin}</td>
              <td className="px-2 py-1 text-right">{row.observed.toLocaleString()}</td>
              <td className="px-2 py-1 text-right">{row.expected.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface StreakComparisonChartProps {
  data: StreakLengthResponse
  isFetching?: boolean
}

export function StreakComparisonChart({ data, isFetching }: StreakComparisonChartProps) {
  const rows = buildStreakRows(data)

  return (
    <ChartCard
      title="Streak length vs. geometric"
      isFetching={isFetching}
      headerExtra={<PValueBadge pValue={data.p_value} />}
      caption={`Chi-square GOF vs. Geometric(p=9/10), n=${data.n_streaks.toLocaleString()} streaks, df=${data.degrees_of_freedom}. Mean length observed ${data.mean_length_observed.toFixed(3)} vs. expected ${data.mean_length_expected.toFixed(3)}. Dashed line = expected count under the geometric null.`}
      chart={
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={rows} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
            <CartesianGrid stroke="var(--gridline)" vertical={false} />
            <XAxis
              dataKey="bin"
              tick={{ fill: "var(--text-muted)", fontSize: 12 }}
              axisLine={{ stroke: "var(--baseline)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "var(--text-muted)", fontSize: 12 }}
              axisLine={{ stroke: "var(--baseline)" }}
              tickLine={false}
              width={48}
            />
            <Tooltip content={StreakTooltip} />
            <Bar dataKey="observed" fill="var(--series-1)" radius={[4, 4, 0, 0]} maxBarSize={24} />
            <Line
              dataKey="expected"
              stroke="var(--text-muted)"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={{ r: 4, fill: "var(--text-muted)", stroke: "var(--surface-1)", strokeWidth: 2 }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      }
      table={<StreakTable rows={rows} />}
    />
  )
}
