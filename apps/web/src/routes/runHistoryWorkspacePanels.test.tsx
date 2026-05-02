import { describe, expect, it, vi } from "vitest";

import type { RunHistoryFilter } from "../controlRoomDefinitions";
import { buildRunHistoryWorkspacePanels, type RunHistoryWorkspaceSectionProps } from "./runHistoryWorkspacePanels";

const emptyFilter: RunHistoryFilter = {
  strategy_id: "",
  strategy_version: "",
  preset_id: "",
  benchmark_family: "",
  tag: "",
  dataset_identity: "",
  filter_expr: "",
  collection_query_label: "",
};

function createPanelInput() {
  return {
    runs: [],
    presets: [],
    runSurfaceCapabilities: null,
    strategies: [],
    filter: emptyFilter,
    setFilter: vi.fn(),
  };
}

describe("buildRunHistoryWorkspacePanels", () => {
  it("assigns research, runtime, and live panels to their route-owned surfaces", () => {
    const calls: RunHistoryWorkspaceSectionProps[] = [];
    const panels = buildRunHistoryWorkspacePanels({
      renderRunSection: (props) => {
        calls.push(props);
        return `${props.surfaceKey}:${props.title}`;
      },
      research: {
        ...createPanelInput(),
      },
      runtime: {
        sandbox: {
          ...createPanelInput(),
        },
        paper: {
          ...createPanelInput(),
        },
      },
      live: {
        ...createPanelInput(),
      },
    });

    expect(calls.map(({ surfaceKey, title }) => `${surfaceKey}:${title}`)).toEqual([
      "backtest:최근 Backtest",
      "sandbox:Sandbox Run",
      "paper:Paper Run",
      "live:Guarded Live Run",
    ]);
    expect(panels.research.runsPanel).toBe("backtest:최근 Backtest");
    expect(panels.runtime.sandboxRunsPanel).toBe("sandbox:Sandbox Run");
    expect(panels.runtime.paperRunsPanel).toBe("paper:Paper Run");
    expect(panels.live.runsPanel).toBe("live:Guarded Live Run");
  });

  it("preserves caller-supplied titles and handlers", () => {
    const onStop = vi.fn();
    const getOrderControls = vi.fn();
    const calls: RunHistoryWorkspaceSectionProps[] = [];
    buildRunHistoryWorkspacePanels({
      renderRunSection: (props) => {
        calls.push(props);
        return null;
      },
      research: {
        ...createPanelInput(),
        title: "Research history",
      },
      runtime: {
        sandbox: {
          ...createPanelInput(),
          title: "Runtime sandbox history",
        },
        paper: {
          ...createPanelInput(),
          title: "Runtime paper history",
        },
      },
      live: {
        ...createPanelInput(),
        title: "Live history",
        onStop,
        getOrderControls,
      },
    });

    expect(calls[0]?.title).toBe("Research history");
    expect(calls[1]?.title).toBe("Runtime sandbox history");
    expect(calls[2]?.title).toBe("Runtime paper history");
    expect(calls[3]?.onStop).toBe(onStop);
    expect(calls[3]?.getOrderControls).toBe(getOrderControls);
  });
});
