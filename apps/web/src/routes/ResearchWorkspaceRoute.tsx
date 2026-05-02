import { ReactNode } from "react";

export type ResearchWorkspaceRouteProps = {
  launchPanel: ReactNode;
  presetPanel: ReactNode;
  referencePanel: ReactNode;
  runsPanel: ReactNode;
};

export function ResearchWorkspaceRoute({
  launchPanel,
  presetPanel,
  referencePanel,
  runsPanel,
}: ResearchWorkspaceRouteProps) {
  return (
    <div className="workspace-panel-grid">
      {launchPanel}
      {presetPanel}
      {referencePanel}
      {runsPanel}
    </div>
  );
}

// Runtime placeholders for generated barrel compatibility.
export const ResearchWorkspaceRouteProps = undefined;
