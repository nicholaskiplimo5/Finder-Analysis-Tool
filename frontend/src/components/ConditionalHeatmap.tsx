import { Fragment, useState } from "react"
import type { ConditionalDigitResponse } from "../api/types"
import { sequentialBlue, textOnSequential } from "../lib/color"
import { formatPercent } from "../lib/format"
import { ChartCard } from "./ChartCard"
import type { HeatmapCell } from "./ConditionalHeatmap.transforms"
import { buildHeatmapCells } from "./ConditionalHeatmap.transforms"
import { PValueBadge } from "./PValueBadge"

function HeatmapGrid({ cells }: { cells: HeatmapCell[] }) {
  const [hovered, setHovered] = useState<HeatmapCell | null>(null)
  const maxProb = Math.max(...cells.map((c) => c.prob), 0.0001)
  const cellByPos = new Map(cells.map((c) => [`${c.row}-${c.col}`, c]))

  return (
    <div>
      <div className="inline-grid gap-0.5" style={{ gridTemplateColumns: "32px repeat(10, 28px)" }}>
        <div />
        {Array.from({ length: 10 }, (_, j) => (
          <div key={`col-${j}`} className="text-center text-xs" style={{ color: "var(--text-muted)" }}>
            {j}
          </div>
        ))}
        {Array.from({ length: 10 }, (_, i) => (
          <Fragment key={`row-${i}`}>
            <div className="flex items-center justify-end pr-1 text-xs" style={{ color: "var(--text-muted)" }}>
              {i}
            </div>
            {Array.from({ length: 10 }, (_, j) => {
              const cell = cellByPos.get(`${i}-${j}`)
              if (!cell) return <div key={`cell-${i}-${j}`} />
              const t = cell.prob / maxProb
              return (
                <button
                  key={`cell-${i}-${j}`}
                  type="button"
                  className="h-7 w-7 rounded-sm text-[10px] font-medium"
                  style={{ backgroundColor: sequentialBlue(t), color: textOnSequential(t) }}
                  onMouseEnter={() => setHovered(cell)}
                  onMouseLeave={() => setHovered(null)}
                  onFocus={() => setHovered(cell)}
                  onBlur={() => setHovered(null)}
                  aria-label={`P(digit ${j} given previous digit ${i}) = ${formatPercent(cell.prob)}, ${cell.count} observations`}
                >
                  {(cell.prob * 100).toFixed(0)}
                </button>
              )
            })}
          </Fragment>
        ))}
      </div>
      <div
        className="mt-2 min-h-[2.5rem] rounded-md border px-3 py-2 text-sm"
        style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)" }}
      >
        {hovered ? (
          <>
            <span className="font-semibold">
              P(d={hovered.col} | prev={hovered.row})
            </span>{" "}
            = <span className="tabular-nums">{formatPercent(hovered.prob)}</span> (95% CI{" "}
            {formatPercent(hovered.ciLow)}-{formatPercent(hovered.ciHigh)}, n={hovered.count.toLocaleString()})
          </>
        ) : (
          <span style={{ color: "var(--text-muted)" }}>Hover or focus a cell for its exact value.</span>
        )}
      </div>
    </div>
  )
}

function HeatmapTable({ cells }: { cells: HeatmapCell[] }) {
  const rowIndices = Array.from(new Set(cells.map((c) => c.row))).sort((a, b) => a - b)
  const colIndices = Array.from(new Set(cells.map((c) => c.col))).sort((a, b) => a - b)
  const cellByPos = new Map(cells.map((c) => [`${c.row}-${c.col}`, c]))

  return (
    <div className="overflow-x-auto">
      <table className="text-sm">
        <caption className="sr-only">Conditional probability P(next digit | previous digit)</caption>
        <thead>
          <tr>
            <th className="px-2 py-1 text-left font-medium" style={{ color: "var(--text-secondary)" }}>
              prev \ next
            </th>
            {colIndices.map((j) => (
              <th key={j} className="px-2 py-1 text-right font-medium" style={{ color: "var(--text-secondary)" }}>
                {j}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {rowIndices.map((i) => (
            <tr key={i} style={{ borderTop: "1px solid var(--gridline)" }}>
              <td className="px-2 py-1 font-medium" style={{ color: "var(--text-secondary)" }}>
                {i}
              </td>
              {colIndices.map((j) => {
                const cell = cellByPos.get(`${i}-${j}`)
                return (
                  <td key={j} className="px-2 py-1 text-right">
                    {cell ? formatPercent(cell.prob) : "-"}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface ConditionalHeatmapProps {
  data: ConditionalDigitResponse
  isFetching?: boolean
}

export function ConditionalHeatmap({ data, isFetching }: ConditionalHeatmapProps) {
  const cells = buildHeatmapCells(data)

  return (
    <ChartCard
      title="Conditional digit distribution P(dₙ | dₙ₋₁)"
      isFetching={isFetching}
      headerExtra={<PValueBadge pValue={data.p_value} />}
      caption={`Chi-square test of independence, n=${data.n_transitions.toLocaleString()} transitions, df=${data.degrees_of_freedom}. Cell shade and label are the row-wise conditional probability; under independence every row should look like the same ~10% pattern.`}
      chart={<HeatmapGrid cells={cells} />}
      table={<HeatmapTable cells={cells} />}
    />
  )
}
