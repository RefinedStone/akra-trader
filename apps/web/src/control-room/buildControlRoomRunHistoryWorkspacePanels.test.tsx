import { describe, expect, it, vi } from "vitest";

import { buildControlRoomRunHistoryWorkspacePanels } from "./buildControlRoomRunHistoryWorkspacePanels";

vi.mock("../features/run-history/RunSection", () => ({
  RunSection: () => null,
}));

function buildModel(overrides: Record<string, unknown> = {}) {
  return {
    backtestRunFilter: {},
    backtests: [],
    cancelLiveOrder: vi.fn(),
    getLiveOrderReplacementDraft: vi.fn(),
    liveRunFilter: {},
    liveRuns: [],
    paperRunFilter: {},
    paperRuns: [],
    presets: [],
    replaceLiveOrder: vi.fn(),
    rerunBacktest: vi.fn(),
    rerunPaper: vi.fn(),
    rerunSandbox: vi.fn(),
    runSurfaceCapabilities: null,
    sandboxRunFilter: {},
    sandboxRuns: [],
    setBacktestRunFilter: vi.fn(),
    setLiveOrderReplacementDraft: vi.fn(),
    setLiveRunFilter: vi.fn(),
    setPaperRunFilter: vi.fn(),
    setSandboxRunFilter: vi.fn(),
    stopLiveRun: vi.fn(),
    stopPaperRun: vi.fn(),
    stopSandboxRun: vi.fn(),
    strategies: [],
    ...overrides,
  };
}

describe("buildControlRoomRunHistoryWorkspacePanels", () => {
  it("keeps the research tab run history free of comparison workspace controls", () => {
    const panels = buildControlRoomRunHistoryWorkspacePanels(buildModel());
    const researchPanel = panels.research.runsPanel as { props: Record<string, unknown> };

    expect(researchPanel.props.surfaceKey).toBe("backtest");
    expect(researchPanel.props.comparison).toBeUndefined();
    expect(researchPanel.props.rerunActions).toHaveLength(3);
  });
});
