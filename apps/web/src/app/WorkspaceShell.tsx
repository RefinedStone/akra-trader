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
  return (
    <div className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Akra Trader / 운영 Control Room</p>
          <h1>Research, Runtime Ops, Guarded Live를 한 화면에서 관리합니다.</h1>
          <p className="hero-copy">
            필요한 작업 영역만 빠르게 확인하고, 실험·운영·실행 제어를 분리해서 처리합니다.
          </p>
        </div>
        <aside className="hero-panel">
          <span className="status-indicator" />
          <strong>{statusText}</strong>
          <p>API base: {apiBase}</p>
          <p>현재 workspace: {activeWorkspaceDescriptor.label}</p>
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
