import { ReactNode } from "react";

export type LiveWorkspaceRouteProps = {
  launchPanel: ReactNode;
  controlPanel: ReactNode;
  runsPanel: ReactNode;
};

export function LiveWorkspaceRoute({
  launchPanel,
  controlPanel,
  runsPanel,
}: LiveWorkspaceRouteProps) {
  return (
    <div className="workspace-panel-grid">
      {launchPanel}
      {controlPanel}
      {runsPanel}
    </div>
  );
}
