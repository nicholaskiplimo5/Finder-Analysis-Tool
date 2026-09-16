import { useEffect, useState } from "react"
import { API_BASE_URL } from "./client"
import type { LiveTick } from "./types"

const MAX_BUFFERED_TICKS = 200

export function useLiveTicks(symbol: string, enabled: boolean) {
  const [ticks, setTicks] = useState<LiveTick[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    if (!symbol || !enabled) {
      setConnected(false)
      return
    }

    setTicks([])
    setConnected(false)

    const url = new URL(`/api/live-ticks/${symbol}`, API_BASE_URL)
    const source = new EventSource(url)

    source.onopen = () => setConnected(true)
    source.onerror = () => setConnected(false)
    source.onmessage = (event: MessageEvent<string>) => {
      const tick = JSON.parse(event.data) as LiveTick
      setTicks((prev) => {
        const next = [tick, ...prev]
        return next.length > MAX_BUFFERED_TICKS ? next.slice(0, MAX_BUFFERED_TICKS) : next
      })
    }

    return () => {
      source.close()
    }
  }, [symbol, enabled])

  return { ticks, connected }
}
