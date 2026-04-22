import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { WorkspaceRouteContent } from "./WorkspaceRouteContent";

function buildRoutes() {
  return {
    overview: { catalogPanel: <div>overview-panel</div> },
    research: {
      launchPanel: <div>research-launch</div>,
      presetPanel: <div>research-preset</div>,
      referencePanel: <div>research-reference</div>,
      runsPanel: <div>research-runs</div>,
    },
    runtime: {
      launchPanel: <div>runtime-launch</div>,
      marketDataPanel: <div>runtime-market-data</div>,
      operatorPanel: <div>runtime-operator</div>,
      sandboxRunsPanel: <div>runtime-sandbox</div>,
      paperRunsPanel: <div>runtime-paper</div>,
    },
    live: {
      launchPanel: <div>live-launch</div>,
      controlPanel: <div>live-control</div>,
      runsPanel: <div>live-runs</div>,
    },
  };
}

describe("WorkspaceRouteContent", () => {
  it("renders overview panels for the overview workspace", () => {
    render(<WorkspaceRouteContent activeWorkspace="overview" routes={buildRoutes()} />);

    expect(screen.getByText("overview-panel")).toBeInTheDocument();
    expect(screen.queryByText("research-launch")).not.toBeInTheDocument();
  });

  it("renders research panels for the research workspace", () => {
    render(<WorkspaceRouteContent activeWorkspace="research" routes={buildRoutes()} />);

    expect(screen.getByText("research-launch")).toBeInTheDocument();
    expect(screen.getByText("research-preset")).toBeInTheDocument();
    expect(screen.queryByText("live-launch")).not.toBeInTheDocument();
  });

  it("renders runtime panels for the runtime workspace", () => {
    render(<WorkspaceRouteContent activeWorkspace="runtime" routes={buildRoutes()} />);

    expect(screen.getByText("runtime-launch")).toBeInTheDocument();
    expect(screen.getByText("runtime-market-data")).toBeInTheDocument();
    expect(screen.queryByText("overview-panel")).not.toBeInTheDocument();
  });

  it("renders live panels for the live workspace", () => {
    render(<WorkspaceRouteContent activeWorkspace="live" routes={buildRoutes()} />);

    expect(screen.getByText("live-launch")).toBeInTheDocument();
    expect(screen.getByText("live-control")).toBeInTheDocument();
    expect(screen.queryByText("runtime-launch")).not.toBeInTheDocument();
  });
});
