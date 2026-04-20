import { ReactNode } from "react";

export type RuntimeWorkspaceRouteProps = {
  launchPanel: ReactNode;
  marketDataPanel: ReactNode;
  operatorPanel: ReactNode;
  sandboxRunsPanel: ReactNode;
  paperRunsPanel: ReactNode;
};

export function RuntimeWorkspaceRoute({
  launchPanel,
  marketDataPanel,
  operatorPanel,
  sandboxRunsPanel,
  paperRunsPanel,
}: RuntimeWorkspaceRouteProps) {
  return (
    <div className="workspace-panel-grid">
      {launchPanel}
      {marketDataPanel}
      {operatorPanel}
      {sandboxRunsPanel}
      {paperRunsPanel}
    </div>
  );
}
