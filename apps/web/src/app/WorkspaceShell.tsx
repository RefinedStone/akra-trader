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
  const marketFocusItems = [
    { label: "주식", value: "Equity" },
    { label: "코인", value: "Crypto" },
    { label: "백테스트", value: "Backtest" },
    { label: "리스크", value: "Risk" },
  ];

  return (
    <div className="shell">
      <header className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Akra Trader / 퀀트 운용 어드민</p>
          <h1>주식·코인 전략을 검증하고 운용하는 퀀트 대시보드</h1>
          <p className="hero-copy">
            백테스트 성과, 시장 데이터 품질, 샌드박스·페이퍼 실행, 실전 보호 장치를
            한 흐름에서 확인합니다.
          </p>
          <div className="hero-action-row" aria-label="주요 운영 상태">
            <span>현재 화면 · {activeWorkspaceDescriptor.label}</span>
            <span>{statusText}</span>
          </div>
          <div className="quant-focus-strip" aria-label="지원 자산과 분석 축">
            {marketFocusItems.map((item) => (
              <span key={item.label}>
                <small>{item.label}</small>
                <strong>{item.value}</strong>
              </span>
            ))}
          </div>
        </div>
        <aside className="hero-panel">
          <div className="hero-panel-status">
            <span className="status-indicator" />
            <strong>{statusText}</strong>
          </div>
          <p>API 기준 주소: {apiBase}</p>
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
