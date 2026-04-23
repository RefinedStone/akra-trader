// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportAuditHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (!selectedProviderProvenanceSchedulerExportJobId) {
    return null;
  }

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Scheduler export audit trail</strong>
        <p>{shortenIdentifier(selectedProviderProvenanceSchedulerExportJobId, 10)}</p>
      </div>
      <RuntimeProviderProvenanceSchedulerExportPolicySection model={model} />
      {providerProvenanceSchedulerExportHistoryLoading ? (
        <p className="empty-state">Loading scheduler export audit trail…</p>
      ) : null}
      {providerProvenanceSchedulerExportHistoryError ? (
        <p className="market-data-workflow-feedback">
          Scheduler export audit failed: {providerProvenanceSchedulerExportHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerExportHistory?.history.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Action</th>
              <th>Actor</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {selectedProviderProvenanceSchedulerExportHistory.history.map((record) => (
              <tr key={`provider-scheduler-export-audit-${record.audit_id}`}>
                <td>{formatTimestamp(record.recorded_at)}</td>
                <td>
                  <strong>{formatWorkflowToken(record.action)}</strong>
                  <p className="run-lineage-symbol-copy">
                    {record.delivery_status
                      ? formatWorkflowToken(record.delivery_status)
                      : "No delivery state recorded."}
                  </p>
                </td>
                <td>
                  <strong>
                    {record.source_tab_label ?? record.requested_by_tab_label ?? "unknown tab"}
                  </strong>
                  <p className="run-lineage-symbol-copy">
                    {record.source_tab_id ?? record.requested_by_tab_id ?? "No tab id recorded."}
                  </p>
                </td>
                <td>
                  <strong>{record.detail}</strong>
                  <p className="run-lineage-symbol-copy">
                    Route {formatWorkflowToken(record.routing_policy_id ?? "default")} ·{" "}
                    {record.routing_targets.length
                      ? record.routing_targets.join(", ")
                      : "no routing targets recorded"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Approval{" "}
                    {record.approval_state
                      ? formatWorkflowToken(record.approval_state)
                      : "not recorded"}{" "}
                    · {record.approval_summary ?? "No approval summary recorded."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {record.delivery_targets.length
                      ? `Targets: ${record.delivery_targets.join(", ")}`
                      : "No delivery targets recorded."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {record.delivery_summary ?? "No delivery summary recorded."}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : selectedProviderProvenanceSchedulerExportHistory &&
        !providerProvenanceSchedulerExportHistoryLoading ? (
        <p className="empty-state">No scheduler export audit events recorded yet.</p>
      ) : null}
    </div>
  );
}
