import { afterEach, describe, expect, it, vi } from "vitest"
import { apiGet, ApiError } from "./client"

describe("apiGet", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("returns parsed JSON on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ hello: "world" }),
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await apiGet<{ hello: string }>("/api/whatever")
    expect(result).toEqual({ hello: "world" })
  })

  it("builds the URL with query params", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) })
    vi.stubGlobal("fetch", fetchMock)

    await apiGet("/api/digit-frequency/R_100", { window: 5000 })

    const calledUrl = fetchMock.mock.calls[0][0] as URL
    expect(calledUrl.pathname).toBe("/api/digit-frequency/R_100")
    expect(calledUrl.searchParams.get("window")).toBe("5000")
  })

  it("throws an ApiError with the backend's detail message on non-2xx", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({ detail: "window too small for max_bin=6" }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await expect(apiGet("/api/streak-length/R_100")).rejects.toThrow("window too small for max_bin=6")
  })

  it("falls back to statusText if the error body has no detail field", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => {
        throw new Error("not json")
      },
    })
    vi.stubGlobal("fetch", fetchMock)

    await expect(apiGet("/api/whatever")).rejects.toThrow("Internal Server Error")
  })

  it("carries the HTTP status on the thrown error for callers that branch on it", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ detail: "unknown symbol: 'NOPE'" }),
    })
    vi.stubGlobal("fetch", fetchMock)

    try {
      await apiGet("/api/digit-frequency/NOPE")
      expect.unreachable("apiGet should have thrown")
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect((error as ApiError).status).toBe(404)
    }
  })
})
