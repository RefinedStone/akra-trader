import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { ControlRoomMarketDataPanel } from "./ControlRoomMarketDataPanel";
import {
  BackfillCountStatus,
  BackfillQualityStatus,
  PanelDisclosure,
  SyncCheckpointStatus,
  SyncFailureStatus,
  buildGapWindowKey,
  instrumentGapRowKey,
  isSameGapWindowSelectionList,
  resolveGapWindowSelectionList,
  toggleExpandedGapRow,
} from "./ControlRoomViewStatusPanels";

function TestDisclosure({
  children,
  summary,
  title,
}: {
  children: ReactNode;
  summary?: string;
  title: string;
}) {
  return (
    <section>
      <h3>{title}</h3>
      {summary ? <p>{summary}</p> : null}
      {children}
    </section>
  );
}

function buildInstrument(overrides: Record<string, unknown> = {}) {
  return {
    backfill_complete: false,
    backfill_completion_ratio: 0.5,
    backfill_contiguous_complete: false,
    backfill_contiguous_completion_ratio: 0.5,
    backfill_contiguous_missing_candles: 2,
    backfill_gap_windows: [
      {
        end_timestamp: "2026-05-04T14:10:00Z",
        missing_candles: 1,
        start_timestamp: "2026-05-04T14:05:00Z",
      },
    ],
    backfill_target_candles: 20,
    candle_count: 10,
    first_timestamp: "2026-05-04T13:00:00Z",
    failure_count_24h: 0,
    instrument_id: "binance:BTC/USDT",
    issues: [],
    lag_seconds: 60,
    last_sync_at: "2026-05-04T14:11:00Z",
    last_timestamp: "2026-05-04T14:10:00Z",
    recent_failures: [],
    sync_checkpoint: null,
    sync_status: "synced",
    timeframe: "5m",
    ...overrides,
  };
}

function buildModel(overrides: Record<string, unknown> = {}) {
  const instrument = buildInstrument();
  return {
    BackfillCountStatus,
    BackfillQualityStatus,
    PanelDisclosure: TestDisclosure,
    SyncCheckpointStatus,
    SyncFailureStatus,
    activeGapWindowPickerRowKey: null,
    activeMarketInstrument: null,
    activeMarketInstrumentKey: null,
    backfillSummary: null,
    buildGapWindowKey,
    buildMarketDataInstrumentFocusKey: (entry: any) => `${entry.instrument_id}:${entry.timeframe}`,
    expandedGapRows: {},
    failureSummary: null,
    focusedMarketWorkflowSummary: null,
    formatCompletion: (value: number | null) => (value === null ? "n/a" : `${Math.round(value * 100)}%`),
    formatTimestamp: (value: string | null) => value ?? "n/a",
    formatWorkflowToken: (value: string | null) => value ?? "n/a",
    handleMarketInstrumentFocus: vi.fn(),
    instrumentGapRowKey,
    isMarketDataInstrumentAtRisk: () => false,
    isSameGapWindowSelectionList,
    marketStatus: {
      instruments: [instrument],
      provider: "binance",
      venue: "binance",
    },
    resolveGapWindowSelectionList,
    setActiveGapWindowPickerRowKey: vi.fn(),
    setExpandedGapRows: vi.fn(),
    setExpandedGapWindowSelections: vi.fn(),
    toggleExpandedGapRow,
    ...overrides,
  };
}

describe("ControlRoomMarketDataPanel", () => {
  it("renders instruments when expanded gap-window selections are missing", () => {
    const model = buildModel({ expandedGapWindowSelections: undefined });

    render(<ControlRoomMarketDataPanel model={model} />);

    expect(screen.getByText("Market data status")).toBeInTheDocument();
    expect(screen.getByText("binance:BTC/USDT")).toBeInTheDocument();
  });
});
