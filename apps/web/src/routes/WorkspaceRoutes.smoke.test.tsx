import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LiveWorkspaceRoute } from "./LiveWorkspaceRoute";
import { MarketsWorkspaceRoute } from "./MarketsWorkspaceRoute";
import { OverviewWorkspaceRoute } from "./OverviewWorkspaceRoute";
import { ResearchWorkspaceRoute } from "./ResearchWorkspaceRoute";
import { RuntimeWorkspaceRoute } from "./RuntimeWorkspaceRoute";

describe("workspace route smoke tests", () => {
  it("renders the overview route", () => {
    render(<OverviewWorkspaceRoute catalogPanel={<div>overview-catalog</div>} />);

    expect(screen.getByText("overview-catalog")).toBeInTheDocument();
  });

  it("renders the research route", () => {
    render(
      <ResearchWorkspaceRoute
        launchPanel={<div>research-launch</div>}
        presetPanel={<div>research-preset</div>}
        referencePanel={<div>research-reference</div>}
        runsPanel={<div>research-runs</div>}
      />,
    );

    expect(screen.getByText("research-launch")).toBeInTheDocument();
    expect(screen.getByText("research-runs")).toBeInTheDocument();
  });

  it("renders the runtime route", () => {
    render(
      <RuntimeWorkspaceRoute
        launchPanel={<div>runtime-launch</div>}
        marketDataPanel={<div>runtime-market-data</div>}
        operatorPanel={<div>runtime-operator</div>}
        sandboxRunsPanel={<div>runtime-sandbox</div>}
        paperRunsPanel={<div>runtime-paper</div>}
      />,
    );

    expect(screen.getByText("runtime-market-data")).toBeInTheDocument();
    expect(screen.getByText("runtime-paper")).toBeInTheDocument();
  });

  it("renders the markets route", () => {
    render(<MarketsWorkspaceRoute chartPanel={<div>markets-chart</div>} />);

    expect(screen.getByText("markets-chart")).toBeInTheDocument();
  });

  it("renders the live route", () => {
    render(
      <LiveWorkspaceRoute
        launchPanel={<div>live-launch</div>}
        controlPanel={<div>live-control</div>}
        runsPanel={<div>live-runs</div>}
      />,
    );

    expect(screen.getByText("live-control")).toBeInTheDocument();
    expect(screen.getByText("live-runs")).toBeInTheDocument();
  });
});
