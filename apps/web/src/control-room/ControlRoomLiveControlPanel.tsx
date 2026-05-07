// @ts-nocheck
import type { ReactNode } from "react";

type LiveControlPanelModel = {
  PanelDisclosure?: any;
  activeGuardedLiveAlertIds?: string[];
  acknowledgeGuardedLiveIncident?: (incidentId: string) => Promise<void>;
  engageGuardedLiveKillSwitch?: () => Promise<void>;
  escalateGuardedLiveIncident?: (incidentId: string) => Promise<void>;
  formatFixedNumber?: (value: number | null | undefined) => string;
  formatTimestamp?: (value: string | null | undefined) => string;
  guardedLive?: any;
  guardedLiveReason?: string;
  guardedLiveSummary?: any;
  recoverGuardedLiveRuntime?: () => Promise<void>;
  releaseGuardedLiveKillSwitch?: () => Promise<void>;
  remediateGuardedLiveIncident?: (incidentId: string) => Promise<void>;
  resumeGuardedLiveRun?: () => Promise<void>;
  runGuardedLiveReconciliation?: () => Promise<void>;
  setGuardedLiveReason?: (value: string) => void;
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

function fallbackTimestamp(value: string | null | undefined) {
  return value ?? "n/a";
}

function fallbackNumber(value: number | null | undefined) {
  return value === null || value === undefined ? "n/a" : String(value);
}

export function ControlRoomLiveControlPanel({ model }: { model: LiveControlPanelModel }) {
  const {
    PanelDisclosure = DefaultDisclosure,
    activeGuardedLiveAlertIds = [],
    acknowledgeGuardedLiveIncident,
    engageGuardedLiveKillSwitch,
    escalateGuardedLiveIncident,
    formatFixedNumber = fallbackNumber,
    formatTimestamp = fallbackTimestamp,
    guardedLive,
    guardedLiveReason = "",
    guardedLiveSummary,
    recoverGuardedLiveRuntime,
    releaseGuardedLiveKillSwitch,
    remediateGuardedLiveIncident,
    resumeGuardedLiveRun,
    runGuardedLiveReconciliation,
    setGuardedLiveReason,
  } = model;

  if (!guardedLive) {
    return (
      <section className="panel panel-wide">
        <p className="kicker">Guarded live</p>
        <h2>Kill switch and reconciliation</h2>
        <p>No guarded-live status loaded.</p>
      </section>
    );
  }

  const blockers = guardedLive.blockers ?? [];
  const findings = guardedLive.reconciliation?.findings ?? [];
  const openOrders = guardedLive.order_book?.open_orders ?? [];
  const incidents = guardedLive.incident_events ?? [];
  const exposures = guardedLive.reconciliation?.venue_snapshot?.exposures ?? [];

  return (
    <section className="panel panel-wide">
      <p className="kicker">Guarded live</p>
      <h2>Kill switch and reconciliation</h2>

      <div className="status-grid">
        <div className="metric-tile">
          <span>Candidacy</span>
          <strong>{guardedLive.candidacy_status}</strong>
        </div>
        <div className="metric-tile">
          <span>Kill switch</span>
          <strong>{guardedLive.kill_switch?.state ?? "n/a"}</strong>
        </div>
        <div className="metric-tile">
          <span>Runtime alerts</span>
          <strong>{guardedLive.active_runtime_alert_count ?? activeGuardedLiveAlertIds.length}</strong>
        </div>
        <div className="metric-tile">
          <span>Venue verification</span>
          <strong>{guardedLive.reconciliation?.venue_snapshot?.verification_state ?? "n/a"}</strong>
        </div>
        <div className="metric-tile">
          <span>Last reconciliation</span>
          <strong>{formatTimestamp(guardedLiveSummary?.latestReconciliationAt ?? null)}</strong>
        </div>
        <div className="metric-tile">
          <span>Blockers</span>
          <strong>{guardedLiveSummary?.blockerCount ?? blockers.length}</strong>
        </div>
        <div className="metric-tile">
          <span>Live owner</span>
          <strong>{guardedLive.ownership?.state ?? "n/a"}</strong>
        </div>
        <div className="metric-tile">
          <span>Open orders</span>
          <strong>{openOrders.length}</strong>
        </div>
      </div>

      <div className="control-action-row">
        <label className="control-action-field">
          <span>Operator reason</span>
          <input
            onChange={(event) => setGuardedLiveReason?.(event.target.value)}
            placeholder="operator_safety_drill"
            type="text"
            value={guardedLiveReason}
          />
        </label>
        <button className="ghost-button" onClick={() => void runGuardedLiveReconciliation?.()} type="button">
          Run reconciliation
        </button>
        <button className="ghost-button" onClick={() => void recoverGuardedLiveRuntime?.()} type="button">
          Recover runtime state
        </button>
        <button className="ghost-button" onClick={() => void resumeGuardedLiveRun?.()} type="button">
          Resume live owner
        </button>
        <button className="ghost-button" onClick={() => void engageGuardedLiveKillSwitch?.()} type="button">
          Engage kill switch
        </button>
        <button className="ghost-button" onClick={() => void releaseGuardedLiveKillSwitch?.()} type="button">
          Release kill switch
        </button>
      </div>

      <div className="panel-disclosure-grid">
        <PanelDisclosure
          defaultOpen={true}
          summary={`${guardedLive.kill_switch?.state ?? "n/a"} kill switch · ${blockers.length} blockers · owner ${guardedLive.ownership?.state ?? "n/a"}`}
          title="Control guardrails"
        >
          <div className="panel-disclosure-stack">
            <table className="data-table">
              <tbody>
                <tr>
                  <th>Kill switch</th>
                  <td>{guardedLive.kill_switch?.state ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>Reason</th>
                  <td>{guardedLive.kill_switch?.reason ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>Owner run</th>
                  <td>{guardedLive.ownership?.owner_run_id ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>Owner session</th>
                  <td>{guardedLive.ownership?.owner_session_id ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>Owner symbol</th>
                  <td>{guardedLive.ownership?.symbol ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>Last order sync</th>
                  <td>{formatTimestamp(guardedLive.ownership?.last_order_sync_at ?? null)}</td>
                </tr>
                <tr>
                  <th>Session restore</th>
                  <td>{guardedLive.session_restore?.state ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>Session handoff</th>
                  <td>{guardedLive.session_handoff?.state ?? "n/a"}</td>
                </tr>
              </tbody>
            </table>

            <h3>Candidate blockers</h3>
            {blockers.length ? (
              <table className="data-table">
                <tbody>
                  {blockers.map((blocker: string) => (
                    <tr key={blocker}>
                      <td>{blocker}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">No guarded-live blockers recorded.</p>
            )}
          </div>
        </PanelDisclosure>

        <PanelDisclosure
          defaultOpen={false}
          summary={`${findings.length} findings · ${openOrders.length} open orders · ${incidents.length} incidents`}
          title="Venue state and incidents"
        >
          <div className="panel-disclosure-stack panel-disclosure-scroll">
            <h3>Reconciliation findings</h3>
            {findings.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Finding</th>
                    <th>Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map((finding: any) => (
                    <tr key={`${finding.kind}-${finding.summary}`}>
                      <td>{finding.severity}</td>
                      <td>{finding.kind}</td>
                      <td>
                        <strong>{finding.summary}</strong>
                        {finding.detail ? <p className="run-lineage-symbol-copy">{finding.detail}</p> : null}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">{guardedLive.reconciliation?.summary ?? "No reconciliation findings."}</p>
            )}

            <h3>Open orders</h3>
            {openOrders.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>Side</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {openOrders.slice(0, 10).map((order: any) => (
                    <tr key={order.order_id}>
                      <td>{order.order_id}</td>
                      <td>{order.side}</td>
                      <td>{formatFixedNumber(order.quantity)}</td>
                      <td>{formatFixedNumber(order.price)}</td>
                      <td>{order.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">No durable open orders.</p>
            )}

            <h3>Exposure</h3>
            {exposures.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Asset</th>
                    <th>Free</th>
                    <th>Locked</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {exposures.map((exposure: any) => (
                    <tr key={exposure.asset}>
                      <td>{exposure.asset}</td>
                      <td>{formatFixedNumber(exposure.free)}</td>
                      <td>{formatFixedNumber(exposure.locked)}</td>
                      <td>{formatFixedNumber(exposure.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">No venue exposure snapshot.</p>
            )}

            <h3>Incidents</h3>
            {incidents.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Severity</th>
                    <th>Summary</th>
                    <th>Updated</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.slice(0, 8).map((incident: any) => (
                    <tr key={incident.incident_id}>
                      <td>{incident.status}</td>
                      <td>{incident.severity}</td>
                      <td>{incident.summary}</td>
                      <td>{formatTimestamp(incident.updated_at ?? null)}</td>
                      <td>
                        <div className="control-action-row">
                          <button
                            className="ghost-button"
                            onClick={() => void acknowledgeGuardedLiveIncident?.(incident.incident_id)}
                            type="button"
                          >
                            Acknowledge
                          </button>
                          <button
                            className="ghost-button"
                            onClick={() => void remediateGuardedLiveIncident?.(incident.incident_id)}
                            type="button"
                          >
                            Remediate
                          </button>
                          <button
                            className="ghost-button"
                            onClick={() => void escalateGuardedLiveIncident?.(incident.incident_id)}
                            type="button"
                          >
                            Escalate
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">No guarded-live incidents.</p>
            )}
          </div>
        </PanelDisclosure>
      </div>
    </section>
  );
}
