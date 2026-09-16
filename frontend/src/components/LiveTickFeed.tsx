import { useLiveTicks } from "../api/useLiveTicks"

interface LiveTickFeedProps {
  symbol: string
}

export function LiveTickFeed({ symbol }: LiveTickFeedProps) {
  const { ticks, connected } = useLiveTicks(symbol, Boolean(symbol))

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)" }}
    >
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-base font-semibold" style={{ color: "var(--text-primary)" }}>
          Live tick feed
        </h3>
        <span className="inline-flex items-center gap-1.5 text-xs" style={{ color: "var(--text-secondary)" }}>
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ backgroundColor: connected ? "var(--status-good)" : "var(--text-muted)" }}
          />
          {connected ? "connected" : "connecting…"}
        </span>
      </div>
      <div className="max-h-72 overflow-y-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ color: "var(--text-secondary)" }}>
              <th className="px-2 py-1 text-left font-medium">Time</th>
              <th className="px-2 py-1 text-right font-medium">Quote</th>
              <th className="px-2 py-1 text-right font-medium">Digit</th>
            </tr>
          </thead>
          <tbody className="tabular-nums">
            {ticks.map((tick) => (
              <tr key={tick.epoch} style={{ borderTop: "1px solid var(--gridline)" }}>
                <td className="px-2 py-1">{new Date(tick.epoch * 1000).toLocaleTimeString()}</td>
                <td className="px-2 py-1 text-right">{tick.quote}</td>
                <td className="px-2 py-1 text-right font-semibold">{tick.digit}</td>
              </tr>
            ))}
            {ticks.length === 0 && (
              <tr>
                <td colSpan={3} className="px-2 py-4 text-center" style={{ color: "var(--text-muted)" }}>
                  Waiting for the next tick…
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
