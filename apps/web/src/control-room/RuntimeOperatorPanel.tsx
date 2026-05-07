// @ts-nocheck
import type { ReactNode } from "react";

type RuntimeOperatorPanelModel = {
  PanelDisclosure?: any;
  formatTimestamp?: (value: string | null | undefined) => string;
  operatorSummary?: {
    alertCount?: number;
    criticalCount?: number;
    deliveryCount?: number;
    historyCount?: number;
    incidentCount?: number;
    latestAuditAt?: string | null;
    warningCount?: number;
  } | null;
  operatorVisibility?: {
    alerts?: Array<{
      alert_id: string;
      category: string;
      detected_at: string | null;
      detail?: string;
      run_id?: string | null;
      severity: string;
      summary: string;
    }>;
    audit_events?: Array<{
      event_id: string;
      action: string;
      actor?: string | null;
      message?: string | null;
      recorded_at: string | null;
    }>;
    incident_events?: Array<{
      incident_id: string;
      status: string;
      severity: string;
      summary: string;
      updated_at: string | null;
    }>;
  } | null;
};

function DefaultDisclosure({
  children,
  summary,
  title,
}: {
  children: ReactNode;
  summary: ReactNode;
  title: string;
}) {
  return (
    <section className="runtime-operator-section">
      <div className="run-lineage-head">
        <span>{title}</span>
        <strong>{summary}</strong>
      </div>
      {children}
    </section>
  );
}

function formatFallbackTimestamp(value: string | null | undefined) {
  return value ?? "n/a";
}

function formatOperatorToken(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  const labels: Record<string, string> = {
    acknowledged: "확인됨",
    audit: "기록",
    critical: "긴급",
    escalated: "전달됨",
    info: "정보",
    open: "열림",
    resolved: "해결됨",
    system: "시스템",
    warning: "주의",
  };
  return labels[value] ?? value.replaceAll("_", " ");
}

export function RuntimeOperatorPanel({ model }: { model: RuntimeOperatorPanelModel }) {
  const {
    PanelDisclosure = DefaultDisclosure,
    formatTimestamp = formatFallbackTimestamp,
    operatorSummary,
    operatorVisibility,
  } = model;
  const alerts = operatorVisibility?.alerts ?? [];
  const auditEvents = operatorVisibility?.audit_events ?? [];
  const incidents = operatorVisibility?.incident_events ?? [];

  return (
    <section className="panel panel-wide">
      <p className="kicker">운영 확인</p>
      <h2>알림과 사고</h2>

      <div className="status-grid">
        <div className="metric-tile">
          <span>활성 알림</span>
          <strong>{operatorSummary?.alertCount ?? alerts.length}</strong>
        </div>
        <div className="metric-tile">
          <span>긴급</span>
          <strong>{operatorSummary?.criticalCount ?? alerts.filter((alert) => alert.severity === "critical").length}</strong>
        </div>
        <div className="metric-tile">
          <span>주의</span>
          <strong>{operatorSummary?.warningCount ?? alerts.filter((alert) => alert.severity === "warning").length}</strong>
        </div>
        <div className="metric-tile">
          <span>최근 기록</span>
          <strong>{formatTimestamp(operatorSummary?.latestAuditAt ?? null)}</strong>
        </div>
        <div className="metric-tile">
          <span>알림 이력</span>
          <strong>{operatorSummary?.historyCount ?? 0}</strong>
        </div>
        <div className="metric-tile">
          <span>사고</span>
          <strong>{operatorSummary?.incidentCount ?? incidents.length}</strong>
        </div>
        <div className="metric-tile">
          <span>전달</span>
          <strong>{operatorSummary?.deliveryCount ?? 0}</strong>
        </div>
      </div>

      <PanelDisclosure
        defaultOpen={true}
        summary={`${alerts.length}개 활성 알림 · ${auditEvents.length}개 최근 기록`}
        title="현재 알림"
      >
        <div className="status-grid-two-column">
          <div>
            <h3>현재 알림</h3>
            {alerts.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>심각도</th>
                    <th>분류</th>
                    <th>내용</th>
                    <th>발견</th>
                    <th>실행</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.alert_id}>
                      <td>{formatOperatorToken(alert.severity)}</td>
                      <td>{formatOperatorToken(alert.category)}</td>
                      <td>
                        <strong>{alert.summary}</strong>
                        {alert.detail ? <p className="run-lineage-symbol-copy">{alert.detail}</p> : null}
                      </td>
                      <td>{formatTimestamp(alert.detected_at)}</td>
                      <td>{alert.run_id ?? "n/a"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="muted-copy">현재 활성 알림이 없습니다.</p>
            )}
          </div>

          <div>
            <h3>최근 기록</h3>
            {auditEvents.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>시간</th>
                    <th>처리</th>
                    <th>담당</th>
                    <th>메시지</th>
                  </tr>
                </thead>
                <tbody>
                  {auditEvents.slice(0, 8).map((event) => (
                    <tr key={event.event_id}>
                      <td>{formatTimestamp(event.recorded_at)}</td>
                      <td>{formatOperatorToken(event.action)}</td>
                      <td>{formatOperatorToken(event.actor ?? "system")}</td>
                      <td>{event.message ?? "n/a"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="muted-copy">최근 기록이 없습니다.</p>
            )}
          </div>
        </div>
      </PanelDisclosure>

      <PanelDisclosure
        defaultOpen={false}
        summary={`${incidents.length}개 사고`}
        title="사고 목록"
      >
        {incidents.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>심각도</th>
                <th>상태</th>
                <th>내용</th>
                <th>갱신</th>
              </tr>
            </thead>
            <tbody>
              {incidents.slice(0, 8).map((incident) => (
                <tr key={incident.incident_id}>
                  <td>{formatOperatorToken(incident.severity)}</td>
                  <td>{formatOperatorToken(incident.status)}</td>
                  <td>{incident.summary}</td>
                  <td>{formatTimestamp(incident.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted-copy">현재 사고가 없습니다.</p>
        )}
      </PanelDisclosure>
    </section>
  );
}
