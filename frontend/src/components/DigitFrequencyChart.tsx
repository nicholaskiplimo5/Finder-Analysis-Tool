import {
  Bar,
  BarChart,
  CartesianGrid,
  ErrorBar,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { TooltipContentProps } from "recharts"
import type { DigitFrequencyResponse } from "../api/types"
import { formatPercent } from "../lib/format"
import { ChartCard } from "./ChartCard"
import type { DigitFrequencyRow } from "./DigitFrequencyChart.transforms"
import { buildDigitFrequencyRows } from "./DigitFrequencyChart.transforms"
import { PValueBadge } from "./PValueBadge"

function DigitFrequencyTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload as DigitFrequencyRow
  return (
    <div
      className="rounded-md border px-3 py-2 text-sm shadow-sm"
      style={{ backgroundColor: "var(--surface-1)", borderColor: "var(--border-ring)", color: "var(--text-primary)" }}
    >
      <div className="font-semibold">Digit {row.digit}</div>
      <div style={{ color: "var(--text-secondary)" }}>
        Observed:{" "}
        <span className="tabular-nums font-medium" style={{ color: "var(--text-primary)" }}>
          {row.observed.toLocaleString()}
        </span>
      </div>
      <div style={{ color: "var(--text-secondary)" }}>
        Expected: <span className="tabular-nums">{row.expected.toFixed(1)}</span>
      </div>
      <div style={{ color: "var(--text-secondary)" }}>
        Proportion: <span className="tabular-nums">{formatPercent(row.proportion)}</span> (95% CI{" "}
        {formatPercent(row.ciLow)}-{formatPercent(row.ciHigh)})
      </div>
    </div>
  )
}

function DigitFrequencyTable({ rows }: { rows: DigitFrequencyRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: "var(--text-secondary)" }}>
            <th className="px-2 py-1 text-left font-medium">Digit</th>
            <th className="px-2 py-1 text-right font-medium">Observed</th>
            <th className="px-2 py-1 text-right font-medium">Expected</th>
            <th className="px-2 py-1 text-right font-medium">Proportion</th>
            <th className="px-2 py-1 text-right font-medium">95% CI</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {rows.map((row) => (
            <tr key={row.digit} style={{ borderTop: "1px solid var(--gridline)" }}>
              <td className="px-2 py-1">{row.digit}</td>
              <td className="px-2 py-1 text-right">{row.observed.toLocaleString()}</td>
              <td className="px-2 py-1 text-right">{row.expected.toFixed(1)}</td>
              <td className="px-2 py-1 text-right">{formatPercent(row.proportion)}</td>
              <td className="px-2 py-1 text-right">
                {formatPercent(row.ciLow)}-{formatPercent(row.ciHigh)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface DigitFrequencyChartProps {
  data: DigitFrequencyResponse
  isFetching?: boolean
}

export function DigitFrequencyChart({ data, isFetching }: DigitFrequencyChartProps) {
  const rows = buildDigitFrequencyRows(data)
  const expectedValue = data.expected_counts[0]

  return (
    <ChartCard
      title="Digit frequency"
      isFetching={isFetching}
      headerExtra={<PValueBadge pValue={data.p_value} />}
      caption={`Chi-square goodness-of-fit vs. uniform, n=${data.n.toLocaleString()}, df=${data.degrees_of_freedom}. Dashed line = expected count under uniform independence (n/10). Error bars are 95% Wilson confidence intervals.`}
      chart={
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={rows} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
            <CartesianGrid stroke="var(--gridline)" vertical={false} />
            <XAxis
              dataKey="digit"
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
            <ReferenceLine
              y={expectedValue}
              stroke="var(--text-muted)"
              strokeDasharray="4 4"
              label={{ value: "expected", position: "insideTopRight", fill: "var(--text-muted)", fontSize: 11 }}
            />
            <Tooltip content={DigitFrequencyTooltip} />
            <Bar dataKey="observed" fill="var(--series-1)" radius={[4, 4, 0, 0]} maxBarSize={24}>
              <ErrorBar dataKey="errorY" width={4} strokeWidth={1} stroke="var(--text-secondary)" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      }
      table={<DigitFrequencyTable rows={rows} />}
    />
  )
}
