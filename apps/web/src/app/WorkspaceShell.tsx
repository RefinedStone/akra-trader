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
  const heroMetrics = controlStripMetrics.slice(0, 4);
  const secondaryMetrics = controlStripMetrics.slice(1, 4);
  const workflowItems = activeWorkspaceDescriptor.sections.slice(0, 4);

  return (
    <div className="shell">
      <header className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Akra Trader / 운용 지휘 콘솔</p>
          <h1>전략 검증부터 실전 보호까지 한 화면에서 판단합니다</h1>
          <p className="hero-copy">
            현재 워크스페이스의 운영 맥락, 핵심 지표, 다음 점검 항목을 먼저 보여주고
            세부 작업면으로 이어갑니다.
          </p>
          <div className="hero-action-row" aria-label="주요 운영 상태">
            <span>
              <small>상태</small>
              <strong>{statusText}</strong>
            </span>
            <span>
              <small>작업면</small>
              <strong>{activeWorkspaceDescriptor.label}</strong>
            </span>
            <span>
              <small>API</small>
              <strong>{apiBase}</strong>
            </span>
          </div>
          <div className="hero-command-grid" aria-label="운영 핵심 지표">
            {(heroMetrics.length > 0 ? heroMetrics : [
              {
                label: activeWorkspaceDescriptor.kicker,
                value: activeWorkspaceDescriptor.summary,
                detail: activeWorkspaceDescriptor.description,
              },
            ]).map((metric) => (
              <article
                className={`hero-command-card ${metric.tone ? `is-${metric.tone}` : ""}`.trim()}
                key={metric.label}
              >
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
                <small>{metric.detail}</small>
              </article>
            ))}
          </div>
        </div>
        <aside className="hero-panel">
          <div className="hero-panel-status">
            <span className="status-indicator" />
            <strong>{activeWorkspaceDescriptor.kicker}</strong>
          </div>
          <p>{activeWorkspaceDescriptor.description}</p>
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
          <div className="hero-workflow-list" aria-label="현재 작업면 점검 항목">
            {workflowItems.map((item, index) => (
              <span key={item}>
                <small>{String(index + 1).padStart(2, "0")}</small>
                <strong>{item}</strong>
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

        <nav className="workspace-nav" aria-label="퀀트 어드민 화면">
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
              최신 데이터 불러오기
            </button>
          </div>
          <div className="workspace-intro-grid">
            <div className="workspace-intro-copy">
              <p>{activeWorkspaceDescriptor.description}</p>
              <strong>{activeWorkspaceDescriptor.summary}</strong>
            </div>
            <div className="workspace-chip-row" aria-label="화면 구성">
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
