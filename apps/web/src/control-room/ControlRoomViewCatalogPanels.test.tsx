import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StrategyColumn } from "./ControlRoomViewCatalogPanels";

function buildStrategy(overrides: Record<string, unknown> = {}) {
  return {
    asset_types: ["spot"],
    catalog_semantics: {
      execution_model: "Verbose execution model copied from adoption docs.",
      operator_notes: ["legacy operator note"],
      parameter_contract: "Large parameter contract",
      source_descriptor: "legacy source descriptor",
      strategy_kind: "standard",
    },
    description: "Simple moving-average strategy.",
    lifecycle: {
      registered_at: "2026-05-01T00:00:00Z",
      stage: "active",
    },
    name: "Moving Average Cross",
    parameter_schema: {
      short_window: {
        default: 8,
        type: "integer",
      },
    },
    runtime: "native",
    strategy_id: "ma_cross_v1",
    supported_timeframes: ["5m"],
    version: "1.0.0",
    version_lineage: ["1.0.0"],
    ...overrides,
  };
}

describe("StrategyColumn", () => {
  it("renders the overview catalog without schema-hint detail blocks", () => {
    render(<StrategyColumn accent="amber" strategies={[buildStrategy()]} title="운용 전략" />);

    expect(screen.getByText("Moving Average Cross")).toBeInTheDocument();
    expect(screen.getByText("ma_cross_v1")).toBeInTheDocument();
    expect(screen.getByText("전략 ID")).toBeInTheDocument();
    expect(screen.getByText("내장 실행")).toBeInTheDocument();
    expect(screen.queryByText("Timeframes")).not.toBeInTheDocument();
    expect(screen.queryByText("Assets")).not.toBeInTheDocument();
    expect(screen.queryByText("Defaults")).not.toBeInTheDocument();
    expect(screen.queryByText("Parameter contract")).not.toBeInTheDocument();
    expect(screen.queryByText("Source")).not.toBeInTheDocument();
    expect(screen.queryByText("Operator notes")).not.toBeInTheDocument();
  });
});
