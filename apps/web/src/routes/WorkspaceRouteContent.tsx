import { ControlWorkspaceId } from "../app/workspaces";
import { LiveWorkspaceRoute, LiveWorkspaceRouteProps } from "./LiveWorkspaceRoute";
import { OverviewWorkspaceRoute, OverviewWorkspaceRouteProps } from "./OverviewWorkspaceRoute";
import { ResearchWorkspaceRoute, ResearchWorkspaceRouteProps } from "./ResearchWorkspaceRoute";
import { RuntimeWorkspaceRoute, RuntimeWorkspaceRouteProps } from "./RuntimeWorkspaceRoute";

export type WorkspaceRoutePanels = {
  live: LiveWorkspaceRouteProps;
  overview: OverviewWorkspaceRouteProps;
  research: ResearchWorkspaceRouteProps;
  runtime: RuntimeWorkspaceRouteProps;
};

export function WorkspaceRouteContent({
  activeWorkspace,
  routes,
}: {
  activeWorkspace: ControlWorkspaceId;
  routes: WorkspaceRoutePanels;
}) {
  if (activeWorkspace === "overview") {
    return <OverviewWorkspaceRoute {...routes.overview} />;
  }
  if (activeWorkspace === "research") {
    return <ResearchWorkspaceRoute {...routes.research} />;
  }
  if (activeWorkspace === "runtime") {
    return <RuntimeWorkspaceRoute {...routes.runtime} />;
  }
  return <LiveWorkspaceRoute {...routes.live} />;
}

// Runtime placeholders for generated barrel compatibility.
export const WorkspaceRoutePanels = undefined;
