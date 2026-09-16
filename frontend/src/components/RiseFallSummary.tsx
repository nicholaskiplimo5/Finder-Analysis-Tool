import type { RiseFallResponse } from "../api/types"
import { PValueBadge } from "./PValueBadge"
import { StatTile } from "./StatTile"

interface RiseFallSummaryProps {
  data: RiseFallResponse
  isFetching?: boolean
}

/** A single test result -- headline numbers, not a chart (per the
 * dataviz skill: "a handful of headline numbers -> KPI row of stat
 * tiles", not a bar chart of two bars). */
export function RiseFallSummary({ data, isFetching }: RiseFallSummaryProps) {
  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)" }}
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-semibold" style={{ color: "var(--text-primary)" }}>
          Rise/fall runs
        </h3>
        <PValueBadge pValue={data.p_value} />
      </div>
      <div className="transition-opacity duration-150" style={{ opacity: isFetching ? 0.6 : 1 }}>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatTile label="Rises" value={data.n_rises.toLocaleString()} />
          <StatTile label="Falls" value={data.n_falls.toLocaleString()} />
          <StatTile label="Runs observed" value={data.n_runs.toLocaleString()} />
          <StatTile
            label="Runs expected"
            value={data.expected_runs.toFixed(1)}
            sublabel={`z = ${data.z_statistic.toFixed(3)}`}
          />
        </div>
      </div>
      <p className="mt-3 text-xs" style={{ color: "var(--text-muted)" }}>
        Wald-Wolfowitz runs test on tick direction. {data.n_ties_dropped.toLocaleString()} tie(s) dropped (no
        direction). Fewer runs than expected suggests clustering; more suggests alternation -- neither is a
        trade recommendation.
      </p>
    </div>
  )
}
