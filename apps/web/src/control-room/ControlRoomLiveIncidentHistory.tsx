// @ts-nocheck

export function ControlRoomLiveIncidentHistory({ model }: { model: any }) {
  const {
    formatTimestamp,
    summarizeProviderRecoveryMarketContextProvenance,
    formatParameterMap,
    formatProviderRecoveryTelemetry,
    formatProviderRecoverySchema,
    guardedLive,
    activeGuardedLiveAlertIds,
    remediateGuardedLiveIncident,
    acknowledgeGuardedLiveIncident,
    escalateGuardedLiveIncident,
  } = model;

  return (
    <>
                  <h3>Guarded-live alerts</h3>
                  {guardedLive.active_alerts.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Category</th>
                          <th>Summary</th>
                          <th>Detected</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.active_alerts.map((alert) => (
                          <tr key={`guarded-live-alert-${alert.alert_id}`}>
                            <td>{alert.severity}</td>
                            <td>{alert.category}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No active guarded-live alerts.</p>
                  )}
                  <h3>Guarded-live alert history</h3>
                  {guardedLive.alert_history.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Status</th>
                          <th>Severity</th>
                          <th>Summary</th>
                          <th>Detected</th>
                          <th>Resolved</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.alert_history.slice(0, 8).map((alert) => (
                          <tr key={`guarded-live-alert-history-${alert.alert_id}`}>
                            <td>{alert.status}</td>
                            <td>{alert.severity}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                            <td>{formatTimestamp(alert.resolved_at ?? null)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live alert history recorded.</p>
                  )}
                  <h3>Guarded-live incidents</h3>
                  {guardedLive.incident_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Kind</th>
                          <th>Severity</th>
                          <th>Summary</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.incident_events.slice(0, 8).map((event) => {
                          const providerRecoveryProvenanceSummary =
                            summarizeProviderRecoveryMarketContextProvenance(
                              event.remediation.provider_recovery,
                            )?.summary ?? null;
                          return (
                          <tr key={`guarded-live-incident-${event.event_id}`}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.kind}</td>
                            <td>{event.severity}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {event.delivery_state}
                                {event.delivery_targets.length ? ` via ${event.delivery_targets.join(", ")}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Ack: {event.acknowledgment_state}
                                {event.acknowledged_by ? ` by ${event.acknowledged_by}` : ""}
                                {event.acknowledged_at ? ` at ${formatTimestamp(event.acknowledged_at)}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Escalation: level {event.escalation_level} / {event.escalation_state}
                                {event.last_escalated_by ? ` by ${event.last_escalated_by}` : ""}
                                {event.last_escalated_at ? ` at ${formatTimestamp(event.last_escalated_at)}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Next escalation: {formatTimestamp(event.next_escalation_at ?? null)}
                                {event.escalation_targets.length ? ` via ${event.escalation_targets.join(", ")}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                External: {event.external_status}
                                {event.external_provider ? ` via ${event.external_provider}` : ""}
                                {event.external_reference ? ` (${event.external_reference})` : ""}
                                {event.external_last_synced_at
                                  ? ` at ${formatTimestamp(event.external_last_synced_at)}`
                                  : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Paging: {event.paging_status}
                                {event.paging_policy_id ? ` via ${event.paging_policy_id}` : ""}
                                {event.paging_provider ? ` (${event.paging_provider})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Provider workflow: {event.provider_workflow_state}
                                {event.provider_workflow_action ? ` / ${event.provider_workflow_action}` : ""}
                                {event.provider_workflow_reference
                                  ? ` (${event.provider_workflow_reference})`
                                  : ""}
                                {event.provider_workflow_last_attempted_at
                                  ? ` at ${formatTimestamp(event.provider_workflow_last_attempted_at)}`
                                  : ""}
                              </p>
                              {event.remediation.state !== "not_applicable" ? (
                                <>
                                  <p className="run-lineage-symbol-copy">
                                    Remediation: {event.remediation.state}
                                    {event.remediation.summary ? ` / ${event.remediation.summary}` : ""}
                                    {event.remediation.runbook ? ` (${event.remediation.runbook})` : ""}
                                    {event.remediation.requested_by
                                      ? ` by ${event.remediation.requested_by}`
                                      : ""}
                                    {event.remediation.last_attempted_at
                                      ? ` at ${formatTimestamp(event.remediation.last_attempted_at)}`
                                      : ""}
                                  </p>
                                  {event.remediation.detail ? (
                                    <p className="run-lineage-symbol-copy">
                                      Remediation detail: {event.remediation.detail}
                                    </p>
                                  ) : null}
                                  {Object.keys(event.remediation.provider_payload).length ? (
                                    <p className="run-lineage-symbol-copy">
                                      Provider recovery payload: {formatParameterMap(event.remediation.provider_payload)}
                                      {event.remediation.provider_payload_updated_at
                                        ? ` at ${formatTimestamp(event.remediation.provider_payload_updated_at)}`
                                        : ""}
                                    </p>
                                  ) : null}
                                  {event.remediation.provider_recovery.lifecycle_state !== "not_synced" ? (
                                    <>
                                      <p className="run-lineage-symbol-copy">
                                        Provider recovery: {event.remediation.provider_recovery.lifecycle_state}
                                        {event.remediation.provider_recovery.job_id
                                          ? ` / job ${event.remediation.provider_recovery.job_id}`
                                          : ""}
                                        {event.remediation.provider_recovery.channels.length
                                          ? ` / channels ${event.remediation.provider_recovery.channels.join(", ")}`
                                          : ""}
                                        {event.remediation.provider_recovery.symbols.length
                                          ? ` / symbols ${event.remediation.provider_recovery.symbols.join(", ")}`
                                          : ""}
                                        {event.remediation.provider_recovery.timeframe
                                          ? ` / ${event.remediation.provider_recovery.timeframe}`
                                          : ""}
                                        {event.remediation.provider_recovery.verification.state !== "unknown"
                                          ? ` / verification ${event.remediation.provider_recovery.verification.state}`
                                          : ""}
                                        {event.remediation.provider_recovery.updated_at
                                          ? ` at ${formatTimestamp(event.remediation.provider_recovery.updated_at)}`
                                          : ""}
                                      </p>
                                      <p className="run-lineage-symbol-copy">
                                        Recovery machine: {event.remediation.provider_recovery.status_machine.state}
                                        {` / workflow ${event.remediation.provider_recovery.status_machine.workflow_state}`}
                                        {event.remediation.provider_recovery.status_machine.workflow_action
                                          ? ` (${event.remediation.provider_recovery.status_machine.workflow_action})`
                                          : ""}
                                        {` / job ${event.remediation.provider_recovery.status_machine.job_state}`}
                                        {` / sync ${event.remediation.provider_recovery.status_machine.sync_state}`}
                                        {event.remediation.provider_recovery.status_machine.attempt_number
                                          ? ` / attempt ${event.remediation.provider_recovery.status_machine.attempt_number}`
                                          : ""}
                                        {event.remediation.provider_recovery.status_machine.last_event_kind
                                          ? ` / event ${event.remediation.provider_recovery.status_machine.last_event_kind}`
                                          : ""}
                                        {event.remediation.provider_recovery.status_machine.last_event_at
                                          ? ` at ${formatTimestamp(event.remediation.provider_recovery.status_machine.last_event_at)}`
                                          : ""}
                                      </p>
                                      {formatProviderRecoveryTelemetry(event.remediation.provider_recovery) ? (
                                        <p className="run-lineage-symbol-copy">
                                          {formatProviderRecoveryTelemetry(event.remediation.provider_recovery)}
                                        </p>
                                      ) : null}
                                      {formatProviderRecoverySchema(event.remediation.provider_recovery) ? (
                                        <p className="run-lineage-symbol-copy">
                                          {formatProviderRecoverySchema(event.remediation.provider_recovery)}
                                        </p>
                                      ) : null}
                                      {providerRecoveryProvenanceSummary ? (
                                        <p className="run-lineage-symbol-copy market-data-provider-provenance-copy">
                                          {providerRecoveryProvenanceSummary}
                                        </p>
                                      ) : null}
                                    </>
                                  ) : null}
                                </>
                              ) : null}
                              {event.acknowledgment_reason ? (
                                <p className="run-lineage-symbol-copy">
                                  Ack reason: {event.acknowledgment_reason}
                                </p>
                              ) : null}
                              {event.escalation_reason ? (
                                <p className="run-lineage-symbol-copy">
                                  Escalation reason: {event.escalation_reason}
                                </p>
                              ) : null}
                            </td>
                            <td>
                              {event.kind === "incident_opened" && activeGuardedLiveAlertIds.has(event.alert_id) ? (
                                <>
                                  {event.remediation.state !== "not_applicable" ? (
                                    <button
                                      className="ghost-button"
                                      onClick={() => void remediateGuardedLiveIncident(event.event_id)}
                                      type="button"
                                    >
                                      Request remediation
                                    </button>
                                  ) : null}
                                  <button
                                    className="ghost-button"
                                    disabled={event.acknowledgment_state === "acknowledged"}
                                    onClick={() => void acknowledgeGuardedLiveIncident(event.event_id)}
                                    type="button"
                                  >
                                    Acknowledge
                                  </button>
                                  <button
                                    className="ghost-button"
                                    onClick={() => void escalateGuardedLiveIncident(event.event_id)}
                                    type="button"
                                  >
                                    Escalate
                                  </button>
                                </>
                              ) : (
                                <span className="run-lineage-symbol-copy">No action</span>
                              )}
                            </td>
                          </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live incident events recorded.</p>
                  )}
                  <h3>Guarded-live delivery history</h3>
                  {guardedLive.delivery_history.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Target</th>
                          <th>Status</th>
                          <th>Attempt</th>
                          <th>Next retry</th>
                          <th>Detail</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.delivery_history.slice(0, 8).map((record) => (
                          <tr key={`guarded-live-delivery-${record.delivery_id}`}>
                            <td>{formatTimestamp(record.attempted_at)}</td>
                            <td>{record.target}</td>
                            <td>{record.status}</td>
                            <td>{record.attempt_number}</td>
                            <td>{formatTimestamp(record.next_retry_at ?? null)}</td>
                            <td>
                              <strong>{record.incident_kind}</strong>
                              <p className="run-lineage-symbol-copy">Phase: {record.phase}</p>
                              {record.provider_action ? (
                                <p className="run-lineage-symbol-copy">
                                  Provider action: {record.provider_action}
                                </p>
                              ) : null}
                              <p className="run-lineage-symbol-copy">
                                External: {record.external_provider ?? "n/a"}
                                {record.external_reference ? ` (${record.external_reference})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">{record.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live outbound delivery attempts recorded.</p>
                  )}
                  <h3>Guarded-live audit</h3>
                  {guardedLive.audit_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Actor</th>
                          <th>Kind</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.audit_events.slice(0, 8).map((event) => (
                          <tr key={event.event_id}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.actor}</td>
                            <td>{event.kind}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live audit events recorded.</p>
                  )}
    </>
  );
}
