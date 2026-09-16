import { keepPreviousData, useQuery } from "@tanstack/react-query"
import type { ApiError } from "./client"
import { apiGet } from "./client"
import type {
  ACFWithCorrectionResponse,
  ConditionalDigitResponse,
  ConditionalDigitSummaryResponse,
  DigitFrequencyResponse,
  DigitFrequencySummaryResponse,
  RiseFallResponse,
  RiseFallSummaryResponse,
  StreakLengthResponse,
  StreakLengthSummaryResponse,
  SymbolInfo,
} from "./types"

export function useSymbols() {
  return useQuery<SymbolInfo[], ApiError>({
    queryKey: ["symbols"],
    queryFn: () => apiGet<SymbolInfo[]>("/api/symbols"),
    staleTime: 60_000,
  })
}

export function useDigitFrequency(symbol: string, windowSize: number) {
  return useQuery<DigitFrequencyResponse, ApiError>({
    queryKey: ["digit-frequency", symbol, windowSize],
    queryFn: () => apiGet<DigitFrequencyResponse>(`/api/digit-frequency/${symbol}`, { window: windowSize }),
    enabled: Boolean(symbol),
    placeholderData: keepPreviousData,
  })
}

export function useDigitFrequencySummary(windowSize: number) {
  return useQuery<DigitFrequencySummaryResponse, ApiError>({
    queryKey: ["digit-frequency-summary", windowSize],
    queryFn: () => apiGet<DigitFrequencySummaryResponse>("/api/digit-frequency", { window: windowSize }),
    placeholderData: keepPreviousData,
  })
}

export function useACF(symbol: string, windowSize: number, maxLag: number) {
  return useQuery<ACFWithCorrectionResponse, ApiError>({
    queryKey: ["acf", symbol, windowSize, maxLag],
    queryFn: () =>
      apiGet<ACFWithCorrectionResponse>(`/api/acf/${symbol}`, { window: windowSize, max_lag: maxLag }),
    enabled: Boolean(symbol),
    placeholderData: keepPreviousData,
  })
}

export function useConditionalDigit(symbol: string, windowSize: number) {
  return useQuery<ConditionalDigitResponse, ApiError>({
    queryKey: ["conditional-digit", symbol, windowSize],
    queryFn: () => apiGet<ConditionalDigitResponse>(`/api/conditional-digit/${symbol}`, { window: windowSize }),
    enabled: Boolean(symbol),
    placeholderData: keepPreviousData,
  })
}

export function useConditionalDigitSummary(windowSize: number) {
  return useQuery<ConditionalDigitSummaryResponse, ApiError>({
    queryKey: ["conditional-digit-summary", windowSize],
    queryFn: () =>
      apiGet<ConditionalDigitSummaryResponse>("/api/conditional-digit", { window: windowSize }),
    placeholderData: keepPreviousData,
  })
}

export function useStreakLength(symbol: string, windowSize: number, maxBin: number) {
  return useQuery<StreakLengthResponse, ApiError>({
    queryKey: ["streak-length", symbol, windowSize, maxBin],
    queryFn: () =>
      apiGet<StreakLengthResponse>(`/api/streak-length/${symbol}`, { window: windowSize, max_bin: maxBin }),
    enabled: Boolean(symbol),
    placeholderData: keepPreviousData,
  })
}

export function useStreakLengthSummary(windowSize: number) {
  return useQuery<StreakLengthSummaryResponse, ApiError>({
    queryKey: ["streak-length-summary", windowSize],
    queryFn: () => apiGet<StreakLengthSummaryResponse>("/api/streak-length", { window: windowSize }),
    placeholderData: keepPreviousData,
  })
}

export function useRiseFall(symbol: string, windowSize: number) {
  return useQuery<RiseFallResponse, ApiError>({
    queryKey: ["rise-fall", symbol, windowSize],
    queryFn: () => apiGet<RiseFallResponse>(`/api/rise-fall/${symbol}`, { window: windowSize }),
    enabled: Boolean(symbol),
    placeholderData: keepPreviousData,
  })
}

export function useRiseFallSummary(windowSize: number) {
  return useQuery<RiseFallSummaryResponse, ApiError>({
    queryKey: ["rise-fall-summary", windowSize],
    queryFn: () => apiGet<RiseFallSummaryResponse>("/api/rise-fall", { window: windowSize }),
    placeholderData: keepPreviousData,
  })
}
