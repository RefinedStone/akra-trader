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
          <p className="eyebrow">Akra Trader / Hexagonal Control Room</p>
          <h1>One control room, split into research, runtime ops, and guarded live workspaces.</h1>
          <p className="hero-copy">
            The backend already exposes research, runtime, and guarded-live surfaces. The frontend
            now routes operators through focused lanes instead of one endless dashboard scroll.
          </p>
        </div>
        <aside className="hero-panel">
          <span className="status-indicator" />
          <strong>{statusText}</strong>
          <p>API base: {apiBase}</p>
          <p>Active workspace: {activeWorkspaceDescriptor.label}</p>
        </aside>
      </header>

      <main className="workspace-shell">
        <section className="control-strip" aria-label="System metrics">
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
              Refresh data
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
