import { ReactNode } from "react";

export type ResearchWorkspaceRouteProps = {
  launchPanel: ReactNode;
  presetPanel: ReactNode;
  runsPanel: ReactNode;
};

export function ResearchWorkspaceRoute({
  launchPanel,
  presetPanel,
  runsPanel,
}: ResearchWorkspaceRouteProps) {
  return (
    <div className="workspace-panel-grid">
      {launchPanel}
      {presetPanel}
      {runsPanel}
    </div>
  );
}

// Runtime placeholders for generated barrel compatibility.
export const ResearchWorkspaceRouteProps = undefined;
