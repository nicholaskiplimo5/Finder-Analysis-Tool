import { useState } from "react"
import type { ReactNode } from "react"

interface ChartCardProps {
  title: string
  caption?: string
  isFetching?: boolean
  headerExtra?: ReactNode
  chart: ReactNode
  table: ReactNode
}

/**
 * Every chart gets a table-view twin (dataviz skill: "no table view /
 * color-only encoding" is an anti-pattern) and holds its previous
 * render at reduced opacity while refetching instead of a skeleton
 * flash or layout jump.
 */
export function ChartCard({ title, caption, isFetching, headerExtra, chart, table }: ChartCardProps) {
  const [view, setView] = useState<"chart" | "table">("chart")

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)" }}
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-semibold" style={{ color: "var(--text-primary)" }}>
          {title}
        </h3>
        <div className="flex items-center gap-3">
          {headerExtra}
          <div className="flex overflow-hidden rounded-md border text-xs" style={{ borderColor: "var(--border-ring)" }}>
            <button
              type="button"
              onClick={() => setView("chart")}
              className="px-2.5 py-1"
              aria-pressed={view === "chart"}
              style={{
                color: view === "chart" ? "var(--text-primary)" : "var(--text-muted)",
                backgroundColor: view === "chart" ? "var(--page-plane)" : "transparent",
              }}
            >
              Chart
            </button>
            <button
              type="button"
              onClick={() => setView("table")}
              className="px-2.5 py-1"
              aria-pressed={view === "table"}
              style={{
                color: view === "table" ? "var(--text-primary)" : "var(--text-muted)",
                backgroundColor: view === "table" ? "var(--page-plane)" : "transparent",
              }}
            >
              Table
            </button>
          </div>
        </div>
      </div>

      <div
        className="transition-opacity duration-150"
        style={{ opacity: isFetching ? 0.6 : 1 }}
      >
        {view === "chart" ? chart : table}
      </div>

      {caption && (
        <p className="mt-2 text-xs" style={{ color: "var(--text-muted)" }}>
          {caption}
        </p>
      )}
    </div>
  )
}
