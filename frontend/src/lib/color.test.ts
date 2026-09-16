import { describe, expect, it } from "vitest"
import { sequentialBlue, textOnSequential } from "./color"

describe("sequentialBlue", () => {
  it("returns the lightest step at t=0 and darkest at t=1", () => {
    expect(sequentialBlue(0).toLowerCase()).toBe("#cde2fb")
    expect(sequentialBlue(1).toLowerCase()).toBe("#0d366b")
  })

  it("clamps out-of-range input instead of extrapolating", () => {
    expect(sequentialBlue(-1)).toBe(sequentialBlue(0))
    expect(sequentialBlue(2)).toBe(sequentialBlue(1))
  })

  it("is monotonically non-increasing in lightness as t increases", () => {
    // A crude monotonicity check: each RGB channel should not increase as
    // we move from light to dark on this particular ramp (light->dark blue).
    const steps = [0, 0.25, 0.5, 0.75, 1].map(sequentialBlue)
    const toRgbSum = (hex: string) => {
      const n = parseInt(hex.replace("#", ""), 16)
      return ((n >> 16) & 255) + ((n >> 8) & 255) + (n & 255)
    }
    const sums = steps.map(toRgbSum)
    for (let i = 1; i < sums.length; i++) {
      expect(sums[i]).toBeLessThanOrEqual(sums[i - 1])
    }
  })
})

describe("textOnSequential", () => {
  it("uses dark ink on light fills and white ink on dark fills", () => {
    expect(textOnSequential(0)).toBe("#0b0b0b")
    expect(textOnSequential(1)).toBe("#ffffff")
  })
})
