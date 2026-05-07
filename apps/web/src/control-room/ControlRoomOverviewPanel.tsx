import type { ControlStripMetric, ControlWorkspaceDescriptor, ControlWorkspaceId } from "../app/workspaces";

type ControlRoomOverviewPanelProps = {
  controlStripMetrics: ControlStripMetric[];
  onNavigate: (workspace: ControlWorkspaceId) => void;
  statusText: string;
  workspaceDescriptors: ControlWorkspaceDescriptor[];
};

export function ControlRoomOverviewPanel({
  controlStripMetrics,
  onNavigate,
  statusText,
  workspaceDescriptors,
}: ControlRoomOverviewPanelProps) {
  const actionWorkspaces = workspaceDescriptors.filter((workspace) => workspace.id !== "overview");
  const primaryMetrics = controlStripMetrics.slice(0, 4);
  const riskMetric =
    controlStripMetrics.find((metric) => metric.tone === "warning") ?? controlStripMetrics[0];

  return (
    <section className="panel panel-wide overview-briefing-panel">
      <div className="section-heading">
        <div>
          <p className="kicker">운영 브리핑</p>
          <h2>오늘의 판단 순서</h2>
        </div>
        <span className="overview-status-pill">{statusText}</span>
      </div>

      <div className="overview-briefing-grid">
        <div className="overview-briefing-main">
          <span>우선 점검</span>
          <strong>{riskMetric?.value ?? "0"}</strong>
          <p>{riskMetric?.detail ?? "활성 운영 지표가 없습니다."}</p>
        </div>

        <div className="overview-metric-stack" aria-label="개요 핵심 지표">
          {primaryMetrics.map((metric) => (
            <article className={`overview-metric-row ${metric.tone ? `is-${metric.tone}` : ""}`.trim()} key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
              <small>{metric.detail}</small>
            </article>
          ))}
        </div>
      </div>

      <div className="overview-action-grid" aria-label="운영 작업면 바로가기">
        {actionWorkspaces.map((workspace) => (
          <button
            className="overview-action-card"
            key={workspace.id}
            onClick={() => onNavigate(workspace.id)}
            type="button"
          >
            <span>{workspace.kicker}</span>
            <strong>{workspace.label}</strong>
            <p>{workspace.summary}</p>
          </button>
        ))}
      </div>
    </section>
  );
}
