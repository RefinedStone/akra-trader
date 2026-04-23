// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportsRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return providerProvenanceSchedulerExportsLoading ? (
    <p className="empty-state">Loading shared scheduler export registry…</p>
  ) : providerProvenanceSchedulerExportsError ? (
    <p className="market-data-workflow-feedback">
      Shared scheduler export registry failed: {providerProvenanceSchedulerExportsError}
    </p>
  ) : providerProvenanceSchedulerExports.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th>Exported</th>
          <th>Status</th>
          <th>Delivery</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerExports.map((entry) => (
          <tr key={`provider-scheduler-export-${entry.job_id}`}>
            <td>
              <strong>{formatTimestamp(entry.exported_at ?? entry.created_at)}</strong>
              <p className="run-lineage-symbol-copy">
                {entry.filter_summary ?? "No scheduler export filter summary recorded."}
              </p>
              <p className="run-lineage-symbol-copy">
                Requested by {entry.requested_by_tab_label ?? entry.requested_by_tab_id ?? "unknown tab"}
              </p>
            </td>
            <td>
              <strong>{entry.result_count} cycle record(s)</strong>
              <p className="run-lineage-symbol-copy">
                Scope {formatWorkflowToken(entry.export_scope)}
              </p>
              <p className="run-lineage-symbol-copy">
                Route {formatWorkflowToken(entry.routing_policy_id ?? "default")} ·{" "}
                {entry.routing_targets.length ? entry.routing_targets.join(", ") : "no targets"}
              </p>
              <p className="run-lineage-symbol-copy">Escalations {entry.escalation_count}</p>
            </td>
            <td>
              <strong>{formatWorkflowToken(entry.last_delivery_status ?? "not_escalated")}</strong>
              <p className="run-lineage-symbol-copy">
                {entry.last_delivery_summary ?? "Not escalated yet."}
              </p>
              <p className="run-lineage-symbol-copy">
                Approval {formatWorkflowToken(entry.approval_state)} ·{" "}
                {entry.approval_summary ?? "No approval summary recorded."}
              </p>
              <p className="run-lineage-symbol-copy">
                {entry.last_escalated_at
                  ? `Last escalated ${formatTimestamp(entry.last_escalated_at)} by ${entry.last_escalated_by ?? "operator"}`
                  : "No escalation recorded."}
              </p>
            </td>
            <td>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  onClick={() => {
                    void copySharedProviderProvenanceSchedulerExport(entry);
                  }}
                  type="button"
                >
                  Copy export
                </button>
                <button
                  className="ghost-button"
                  onClick={() => {
                    void loadProviderProvenanceSchedulerExportHistory(entry.job_id);
                  }}
                  type="button"
                >
                  View history
                </button>
                <button
                  className="ghost-button"
                  onClick={() => {
                    void escalateSharedProviderProvenanceSchedulerExport(entry);
                  }}
                  disabled={entry.approval_required && entry.approval_state !== "approved"}
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
    <p className="empty-state">No shared scheduler exports have been recorded yet.</p>
  );
}
