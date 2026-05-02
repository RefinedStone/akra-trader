import { ReactNode } from "react";

export type OverviewWorkspaceRouteProps = {
  catalogPanel: ReactNode;
};

export function OverviewWorkspaceRoute({
  catalogPanel,
}: OverviewWorkspaceRouteProps) {
  return (
    <div className="workspace-panel-grid">
      {catalogPanel}
    </div>
  );
}

// Runtime placeholders for generated barrel compatibility.
export const OverviewWorkspaceRouteProps = undefined;
