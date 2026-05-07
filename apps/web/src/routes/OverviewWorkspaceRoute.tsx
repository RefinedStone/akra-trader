import { ReactNode } from "react";

export type OverviewWorkspaceRouteProps = {
  briefingPanel: ReactNode;
  catalogPanel: ReactNode;
};

export function OverviewWorkspaceRoute({
  briefingPanel,
  catalogPanel,
}: OverviewWorkspaceRouteProps) {
  return (
    <div className="workspace-panel-grid">
      {briefingPanel}
      {catalogPanel}
    </div>
  );
}

// Runtime placeholders for generated barrel compatibility.
export const OverviewWorkspaceRouteProps = undefined;
