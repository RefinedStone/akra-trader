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
      <p className="kicker">Operator trust</p>
      <h2>Runtime alerts and audit</h2>

      <div className="status-grid">
        <div className="metric-tile">
          <span>Active alerts</span>
          <strong>{operatorSummary?.alertCount ?? alerts.length}</strong>
        </div>
        <div className="metric-tile">
          <span>Critical</span>
          <strong>{operatorSummary?.criticalCount ?? alerts.filter((alert) => alert.severity === "critical").length}</strong>
        </div>
        <div className="metric-tile">
          <span>Warnings</span>
          <strong>{operatorSummary?.warningCount ?? alerts.filter((alert) => alert.severity === "warning").length}</strong>
        </div>
        <div className="metric-tile">
          <span>Latest audit</span>
          <strong>{formatTimestamp(operatorSummary?.latestAuditAt ?? null)}</strong>
        </div>
        <div className="metric-tile">
          <span>Alert history</span>
          <strong>{operatorSummary?.historyCount ?? 0}</strong>
        </div>
        <div className="metric-tile">
          <span>Incidents</span>
          <strong>{operatorSummary?.incidentCount ?? incidents.length}</strong>
        </div>
        <div className="metric-tile">
          <span>Deliveries</span>
          <strong>{operatorSummary?.deliveryCount ?? 0}</strong>
        </div>
      </div>

      <PanelDisclosure
        defaultOpen={true}
        summary={`${alerts.length} active alerts · ${auditEvents.length} recent audit events`}
        title="Active alerts and audit"
      >
        <div className="status-grid-two-column">
          <div>
            <h3>Active alerts</h3>
            {alerts.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Category</th>
                    <th>Summary</th>
                    <th>Detected</th>
                    <th>Run</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.alert_id}>
                      <td>{alert.severity}</td>
                      <td>{alert.category}</td>
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
              <p className="muted-copy">No active runtime alerts.</p>
            )}
          </div>

          <div>
            <h3>Recent audit</h3>
            {auditEvents.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Action</th>
                    <th>Actor</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {auditEvents.slice(0, 8).map((event) => (
                    <tr key={event.event_id}>
                      <td>{formatTimestamp(event.recorded_at)}</td>
                      <td>{event.action}</td>
                      <td>{event.actor ?? "system"}</td>
                      <td>{event.message ?? "n/a"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="muted-copy">No recent audit events.</p>
            )}
          </div>
        </div>
      </PanelDisclosure>

      <PanelDisclosure
        defaultOpen={false}
        summary={`${incidents.length} incidents`}
        title="Incident queue"
      >
        {incidents.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Status</th>
                <th>Summary</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {incidents.slice(0, 8).map((incident) => (
                <tr key={incident.incident_id}>
                  <td>{incident.severity}</td>
                  <td>{incident.status}</td>
                  <td>{incident.summary}</td>
                  <td>{formatTimestamp(incident.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted-copy">No runtime incidents.</p>
        )}
      </PanelDisclosure>
    </section>
  );
}
