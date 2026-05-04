import { ReactNode } from "react";
import { ControlStripMetric, ControlWorkspaceDescriptor, ControlWorkspaceId } from "./workspaces";

type WorkspaceShellProps = {
  activeWorkspace: ControlWorkspaceId;
  activeWorkspaceDescriptor: ControlWorkspaceDescriptor;
  apiBase: string;
  children: ReactNode;
  controlStripMetrics: ControlStripMetric[];
  onNavigate: (workspace: ControlWorkspaceId) => void;
  onRefresh: () => void;
  statusText: string;
  workspaceDescriptors: ControlWorkspaceDescriptor[];
};

export function WorkspaceShell({
  activeWorkspace,
  activeWorkspaceDescriptor,
  apiBase,
  children,
  controlStripMetrics,
  onNavigate,
  onRefresh,
  statusText,
  workspaceDescriptors,
}: WorkspaceShellProps) {
  const primaryMetric = controlStripMetrics[0];
  const secondaryMetrics = controlStripMetrics.slice(1, 3);

  return (
    <div className="shell">
      <header className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Akra Trader / 운영 Control Room</p>
          <h1>Trading operations command center</h1>
          <p className="hero-copy">
            실험, 시장 데이터, runtime, guarded live를 분리된 workspace로 운영하되
            핵심 상태는 한 화면에서 판단합니다.
          </p>
          <div className="hero-action-row" aria-label="주요 운영 상태">
            <span>Active workspace · {activeWorkspaceDescriptor.label}</span>
            <span>{statusText}</span>
          </div>
        </div>
        <aside className="hero-panel">
          <div className="hero-panel-status">
            <span className="status-indicator" />
            <strong>{statusText}</strong>
          </div>
          <p>API base: {apiBase}</p>
          {primaryMetric ? (
            <div className="hero-primary-metric">
              <span>{primaryMetric.label}</span>
              <strong>{primaryMetric.value}</strong>
              <small>{primaryMetric.detail}</small>
            </div>
          ) : null}
          <div className="hero-mini-metrics">
            {secondaryMetrics.map((metric) => (
              <span key={metric.label}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
              </span>
            ))}
          </div>
        </aside>
      </header>

      <main className="workspace-shell">
        <section className="control-strip" aria-label="시스템 지표">
          {controlStripMetrics.map((metric) => (
            <article
              className={`control-metric-card ${metric.tone ? `is-${metric.tone}` : ""}`.trim()}
              key={metric.label}
            >
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
              <small>{metric.detail}</small>
            </article>
          ))}
        </section>

        <nav className="workspace-nav" aria-label="Control room workspaces">
          {workspaceDescriptors.map((workspace) => (
            <button
              aria-pressed={activeWorkspace === workspace.id}
              className={`workspace-tab ${activeWorkspace === workspace.id ? "is-active" : ""}`.trim()}
              key={workspace.id}
              onClick={() => onNavigate(workspace.id)}
              type="button"
            >
              <span className="workspace-tab-kicker">{workspace.kicker}</span>
              <strong>{workspace.label}</strong>
              <span className="workspace-tab-summary">{workspace.summary}</span>
            </button>
          ))}
        </nav>

        <section className="panel panel-wide workspace-intro-panel">
          <div className="workspace-intro-head">
            <div>
              <p className="kicker">{activeWorkspaceDescriptor.kicker}</p>
              <h2>{activeWorkspaceDescriptor.label}</h2>
            </div>
            <button className="ghost-button" onClick={onRefresh} type="button">
              데이터 새로고침
            </button>
          </div>
          <div className="workspace-intro-grid">
            <div className="workspace-intro-copy">
              <p>{activeWorkspaceDescriptor.description}</p>
              <strong>{activeWorkspaceDescriptor.summary}</strong>
            </div>
            <div className="workspace-chip-row" aria-label="Workspace surfaces">
              {activeWorkspaceDescriptor.sections.map((section) => (
                <span className="workspace-chip" key={section}>
                  {section}
                </span>
              ))}
            </div>
          </div>
          {activeWorkspace === "overview" ? (
            <div className="workspace-route-grid">
              {workspaceDescriptors
                .filter((workspace) => workspace.id !== "overview")
                .map((workspace) => (
                  <button
                    className="workspace-route-card"
                    key={workspace.id}
                    onClick={() => onNavigate(workspace.id)}
                    type="button"
                  >
                    <span>{workspace.kicker}</span>
                    <strong>{workspace.label}</strong>
                    <p>{workspace.description}</p>
                    <small>{workspace.summary}</small>
                  </button>
                ))}
            </div>
          ) : null}
        </section>

        {children}
      </main>
    </div>
  );
}
