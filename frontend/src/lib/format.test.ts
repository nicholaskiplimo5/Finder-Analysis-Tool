import { describe, expect, it } from "vitest"
import { formatCompact, formatPercent, formatPValue } from "./format"

describe("formatPercent", () => {
  it("formats a proportion as a percentage with default 1 decimal", () => {
    expect(formatPercent(0.1)).toBe("10.0%")
    expect(formatPercent(0.12345)).toBe("12.3%")
  })

  it("respects a custom digit count", () => {
    expect(formatPercent(0.12345, 3)).toBe("12.345%")
  })
})

describe("formatPValue", () => {
  it("shows p = x.xxxx for ordinary values", () => {
    expect(formatPValue(0.0421)).toBe("p = 0.0421")
    expect(formatPValue(0.5)).toBe("p = 0.5000")
  })

  it("floors to p < 0.0001 rather than showing 0.0000", () => {
    expect(formatPValue(0)).toBe("p < 0.0001")
    expect(formatPValue(0.00001)).toBe("p < 0.0001")
  })
})

describe("formatCompact", () => {
  it("compacts large numbers", () => {
    expect(formatCompact(1284)).toBe("1.3K")
    expect(formatCompact(4_200_000)).toBe("4.2M")
  })

  it("leaves small numbers alone", () => {
    expect(formatCompact(42)).toBe("42")
  })
})
