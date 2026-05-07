import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { ControlRoomRoutes } from "./ControlRoomRoutes";

function WorkspaceShell({ children }: { children: ReactNode }) {
  return <div>{children}</div>;
}

function WorkspaceRouteContent({ routes }: { routes: any }) {
  return (
    <div>
      {routes.overview.briefingPanel}
      {routes.overview.catalogPanel}
      {routes.research.launchPanel}
      {routes.runtime.launchPanel}
      {routes.live.launchPanel}
    </div>
  );
}

function RunForm() {
  return <div>run-form</div>;
}

function PresetCatalogPanel() {
  return <div>preset-catalog</div>;
}

function StrategyColumn({ title }: { title: string }) {
  return <div>{title}</div>;
}

function buildModel() {
  const base = {
    PresetCatalogPanel,
    RunForm,
    StrategyColumn,
    WorkspaceRouteContent,
    WorkspaceShell,
    activeWorkspace: "overview",
    activeWorkspaceDescriptor: { id: "overview", label: "Overview" },
    apiBase: "/api",
    applyPresetLifecycleAction: vi.fn(),
    backtestForm: {},
    beginPresetEdit: vi.fn(),
    controlStripMetrics: [],
    editingPresetId: null,
    expandedPresetRevisionIds: {},
    handleBacktestSubmit: vi.fn(),
    handleLiveSubmit: vi.fn(),
    handlePresetSubmit: vi.fn(),
    handleSandboxSubmit: vi.fn(),
    liveForm: {},
    loadAll: vi.fn(),
    navigateToWorkspace: vi.fn(),
    presetForm: {},
    presets: [],
    resetPresetEditor: vi.fn(),
    restorePresetRevision: vi.fn(),
    runHistoryWorkspacePanels: {
      live: { runsPanel: <div>live-runs</div> },
      research: { runsPanel: <div>research-runs</div> },
      runtime: {
        paperRunsPanel: <div>paper-runs</div>,
        sandboxRunsPanel: <div>sandbox-runs</div>,
      },
    },
    runSurfaceCapabilities: null,
    sandboxForm: {},
    setBacktestForm: vi.fn(),
    setLiveForm: vi.fn(),
    setPresetForm: vi.fn(),
    setSandboxForm: vi.fn(),
    statusText: "ready",
    strategies: [{ runtime: "native" }],
    strategyGroups: { future: [], native: [] },
    togglePresetRevisions: vi.fn(),
    workspaceDescriptors: [
      {
        id: "overview",
        kicker: "Overview",
        label: "Overview",
        description: "Overview",
        summary: "Overview",
        sections: [],
      },
    ],
  };

  return new Proxy(base, {
    get(target, prop) {
      if (typeof prop === "string" && prop.toLowerCase().includes("providerprovenance")) {
        throw new Error(`unexpected provider provenance route binding: ${prop}`);
      }
      return target[prop as keyof typeof target];
    },
  });
}

describe("ControlRoomRoutes", () => {
  it("composes workspace tabs without touching provider-provenance route bindings", () => {
    render(<ControlRoomRoutes model={buildModel()} />);

    expect(screen.getByText("오늘의 판단 순서")).toBeInTheDocument();
    expect(screen.getByText("전략 운영 카탈로그")).toBeInTheDocument();
    expect(screen.queryByText("Strategy Catalog")).not.toBeInTheDocument();
    expect(screen.queryByText("Start sandbox worker")).not.toBeInTheDocument();
    expect(screen.queryByText("Guarded Live")).not.toBeInTheDocument();
    expect(screen.getAllByText("run-form")).toHaveLength(3);
  });
});
