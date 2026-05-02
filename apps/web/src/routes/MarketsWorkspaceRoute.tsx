import { ReactNode } from "react";

export type MarketsWorkspaceRouteProps = {
  chartPanel: ReactNode;
};

export function MarketsWorkspaceRoute({ chartPanel }: MarketsWorkspaceRouteProps) {
  return <div className="workspace-panel-grid">{chartPanel}</div>;
}

// Runtime placeholders for generated barrel compatibility.
export const MarketsWorkspaceRouteProps = undefined;
