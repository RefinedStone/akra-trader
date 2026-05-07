import { describe, expect, it, vi } from "vitest";

import {
  buildControlRoomRunHistoryWorkspacePanels,
  isLegacyReferenceRun,
} from "./buildControlRoomRunHistoryWorkspacePanels";

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
    expect(researchPanel.props.runSurfaceCapabilities).toBeNull();
    expect(researchPanel.props.rerunActions).toHaveLength(3);
    expect(researchPanel.props.rerunActions).toMatchObject([
      { label: "백테스트 다시 실행" },
      { label: "테스트 실행으로 확인" },
      { label: "모의 주문으로 확인" },
    ]);
  });

  it("keeps runtime and live run histories free of capability contract details", () => {
    const panels = buildControlRoomRunHistoryWorkspacePanels(buildModel());
    const sandboxPanel = panels.runtime.sandboxRunsPanel as { props: Record<string, unknown> };
    const paperPanel = panels.runtime.paperRunsPanel as { props: Record<string, unknown> };
    const livePanel = panels.live.runsPanel as { props: Record<string, unknown> };

    expect(sandboxPanel.props.runSurfaceCapabilities).toBeNull();
    expect(paperPanel.props.runSurfaceCapabilities).toBeNull();
    expect(livePanel.props.runSurfaceCapabilities).toBeNull();
  });

  it("filters legacy third-party reference runs out of visible histories", () => {
    const panels = buildControlRoomRunHistoryWorkspacePanels(buildModel({
      backtests: [
        {
          config: {
            run_id: "legacy-run",
            strategy_id: "nfi_x7_referenceBTC/USDT",
            strategy_version: "v17.3.1107",
          },
          provenance: { lane: "native", strategy: { runtime: "native" } },
        },
        {
          config: {
            run_id: "native-run",
            strategy_id: "ma_cross_v1",
            strategy_version: "1.0.0",
          },
          provenance: { lane: "native", strategy: { runtime: "native" } },
        },
      ],
    }));
    const researchPanel = panels.research.runsPanel as { props: Record<string, any> };

    expect(researchPanel.props.runs.map((run: any) => run.config.run_id)).toEqual(["native-run"]);
  });

  it("detects legacy reference provenance even when the strategy id was normalized", () => {
    expect(isLegacyReferenceRun({
      config: { run_id: "legacy-run", strategy_id: "ma_cross_v1" },
      provenance: { lane: "native", strategy: { runtime: "freqtrade_reference" } },
    })).toBe(true);
  });
});
