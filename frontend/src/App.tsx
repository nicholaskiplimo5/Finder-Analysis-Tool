import { useState } from "react"
import type { ReactNode } from "react"
import type { UseQueryResult } from "@tanstack/react-query"
import type { ApiError } from "./api/client"
import {
  useACF,
  useConditionalDigit,
  useDigitFrequency,
  useRiseFall,
  useStreakLength,
  useSymbols,
} from "./api/hooks"
import { ACFChart } from "./components/ACFChart"
import { ConditionalHeatmap } from "./components/ConditionalHeatmap"
import { DigitFrequencyChart } from "./components/DigitFrequencyChart"
import { FilterBar } from "./components/FilterBar"
import { LiveTickFeed } from "./components/LiveTickFeed"
import { RiseFallSummary } from "./components/RiseFallSummary"
import { StreakComparisonChart } from "./components/StreakComparisonChart"

function Card({ children }: { children: ReactNode }) {
  return (
    <div
      className="rounded-lg border p-4 text-sm"
      style={{ borderColor: "var(--border-ring)", backgroundColor: "var(--surface-1)", color: "var(--text-secondary)" }}
    >
      {children}
    </div>
  )
}

function QuerySection<T>({
  query,
  label,
  render,
}: {
  query: UseQueryResult<T, ApiError>
  label: string
  render: (data: T, isFetching: boolean) => ReactNode
}) {
  if (query.isPending) return <Card>Loading {label}…</Card>
  if (query.isError) {
    return (
      <Card>
        {label}: {query.error.message}
      </Card>
    )
  }
  return <>{render(query.data, query.isFetching)}</>
}

export default function App() {
  const symbolsQuery = useSymbols()
  // `symbolOverride` is only set once the user actually picks a symbol.
  // Until then, the effective symbol is derived from the first loaded
  // entry -- no effect needed to "sync" state that render can compute
  // directly from the query result.
  const [symbolOverride, setSymbolOverride] = useState<string | null>(null)
  const symbol = symbolOverride ?? symbolsQuery.data?.[0]?.symbol ?? ""
  const [windowSize, setWindowSize] = useState(5000)
  const [maxLag, setMaxLag] = useState(20)
  const [maxBin, setMaxBin] = useState(4)

  const digitFrequencyQuery = useDigitFrequency(symbol, windowSize)
  const acfQuery = useACF(symbol, windowSize, maxLag)
  const conditionalDigitQuery = useConditionalDigit(symbol, windowSize)
  const streakLengthQuery = useStreakLength(symbol, windowSize, maxBin)
  const riseFallQuery = useRiseFall(symbol, windowSize)

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <header className="mb-6">
        <h1 className="text-xl font-semibold" style={{ color: "var(--text-primary)" }}>
          Finder Analysis Tool
        </h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Measures whether patterns exist in Deriv synthetic-index digit and tick streams. Every statistic
          below ships a p-value or confidence interval. This is not a signal generator: nothing here is a
          trade recommendation.
        </p>
      </header>

      <div className="mb-6">
        <FilterBar
          symbols={symbolsQuery.data ?? []}
          symbol={symbol}
          onSymbolChange={setSymbolOverride}
          windowSize={windowSize}
          onWindowSizeChange={setWindowSize}
          maxLag={maxLag}
          onMaxLagChange={setMaxLag}
          maxBin={maxBin}
          onMaxBinChange={setMaxBin}
        />
      </div>

      {!symbol ? (
        <Card>No symbols available yet -- waiting on the ingestion service.</Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <QuerySection
            query={digitFrequencyQuery}
            label="digit frequency"
            render={(data, isFetching) => <DigitFrequencyChart data={data} isFetching={isFetching} />}
          />
          <QuerySection
            query={acfQuery}
            label="ACF"
            render={(data, isFetching) => <ACFChart data={data} isFetching={isFetching} />}
          />
          <QuerySection
            query={conditionalDigitQuery}
            label="conditional digit distribution"
            render={(data, isFetching) => <ConditionalHeatmap data={data} isFetching={isFetching} />}
          />
          <QuerySection
            query={streakLengthQuery}
            label="streak length"
            render={(data, isFetching) => <StreakComparisonChart data={data} isFetching={isFetching} />}
          />
          <QuerySection
            query={riseFallQuery}
            label="rise/fall runs"
            render={(data, isFetching) => <RiseFallSummary data={data} isFetching={isFetching} />}
          />
          <LiveTickFeed symbol={symbol} />
        </div>
      )}
    </div>
  )
}
