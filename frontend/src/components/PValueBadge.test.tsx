import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { PValueBadge } from "./PValueBadge"

describe("PValueBadge", () => {
  it("states the p-value and threshold in text, below alpha", () => {
    render(<PValueBadge pValue={0.001} alpha={0.05} />)
    expect(screen.getByText("p = 0.0010")).toBeInTheDocument()
    expect(screen.getByText("below α=0.05")).toBeInTheDocument()
  })

  it("states the p-value and threshold in text, above alpha", () => {
    render(<PValueBadge pValue={0.6} alpha={0.05} />)
    expect(screen.getByText("p = 0.6000")).toBeInTheDocument()
    expect(screen.getByText("above α=0.05")).toBeInTheDocument()
  })

  it("shows the corrected p-value alongside the raw one when provided", () => {
    render(<PValueBadge pValue={0.001} correctedPValue={0.02} correctionMethod="holm" />)
    expect(screen.getByText(/holm: p = 0.0200/)).toBeInTheDocument()
  })

  // This is a project requirement, not a style preference: the tool must
  // never imply a trading signal, so a "significant" result must not be
  // painted with an alarm/success color -- it stays in neutral ink with
  // a plain border, distinguished only by its text.
  it("never uses a status (red/green) color regardless of significance", () => {
    const { container: belowAlphaContainer } = render(<PValueBadge pValue={0.0001} />)
    const { container: aboveAlphaContainer } = render(<PValueBadge pValue={0.9} />)

    for (const container of [belowAlphaContainer, aboveAlphaContainer]) {
      const badge = container.querySelector("span")!
      const inlineStyles = Array.from(container.querySelectorAll("[style]")).map(
        (el) => (el as HTMLElement).style.color + (el as HTMLElement).style.borderColor,
      )
      expect(badge).toBeInTheDocument()
      for (const style of inlineStyles) {
        expect(style).not.toMatch(/#0ca30c|#d03b3b|status-good|status-critical/i)
      }
    }
  })
})
