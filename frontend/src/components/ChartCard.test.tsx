import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import { ChartCard } from "./ChartCard"

describe("ChartCard", () => {
  it("shows the chart view by default and can toggle to the table view", async () => {
    const user = userEvent.setup()
    render(
      <ChartCard
        title="Test chart"
        chart={<div data-testid="chart-view">chart content</div>}
        table={<div data-testid="table-view">table content</div>}
      />,
    )

    expect(screen.getByTestId("chart-view")).toBeInTheDocument()
    expect(screen.queryByTestId("table-view")).not.toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "Table" }))

    expect(screen.getByTestId("table-view")).toBeInTheDocument()
    expect(screen.queryByTestId("chart-view")).not.toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "Chart" }))
    expect(screen.getByTestId("chart-view")).toBeInTheDocument()
  })

  it("reduces opacity while fetching, without unmounting the content (no skeleton flash)", () => {
    const { rerender, container } = render(
      <ChartCard title="Test chart" isFetching={false} chart={<div>content</div>} table={<div>table</div>} />,
    )
    const wrapper = container.querySelector(".transition-opacity") as HTMLElement
    expect(wrapper.style.opacity).toBe("1")

    rerender(<ChartCard title="Test chart" isFetching chart={<div>content</div>} table={<div>table</div>} />)
    expect(wrapper.style.opacity).toBe("0.6")
    expect(screen.getByText("content")).toBeInTheDocument()
  })
})
