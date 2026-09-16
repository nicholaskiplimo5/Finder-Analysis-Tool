interface StatTileProps {
  label: string
  value: string
  sublabel?: string
}

/** Stat-tile contract per the dataviz skill: sentence-case label, no
 * trailing colon, semibold proportional-figure value (never
 * tabular-nums on a standalone display value). No color-coded delta --
 * there is no "good" or "bad" direction for these statistics. */
export function StatTile({ label, value, sublabel }: StatTileProps) {
  return (
    <div
      className="rounded-lg border px-4 py-3"
      style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)" }}
    >
      <div className="text-sm" style={{ color: "var(--text-secondary)" }}>
        {label}
      </div>
      <div className="text-2xl font-semibold" style={{ color: "var(--text-primary)" }}>
        {value}
      </div>
      {sublabel && (
        <div className="text-xs" style={{ color: "var(--text-muted)" }}>
          {sublabel}
        </div>
      )}
    </div>
  )
}
