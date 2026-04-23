// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Shared scheduler exports</strong>
        <p>
          {providerProvenanceSchedulerExports.length
            ? `${providerProvenanceSchedulerExports.length} server-side scheduler export snapshot(s) are available.`
            : "No shared scheduler exports have been recorded yet."}
        </p>
      </div>
      {providerProvenanceSchedulerExportsLoading ? (
        <p className="empty-state">Loading shared scheduler export registry…</p>
      ) : null}
      {providerProvenanceSchedulerExportsError ? (
        <p className="market-data-workflow-feedback">
          Shared scheduler export registry failed: {providerProvenanceSchedulerExportsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerExports.length ? (
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
                    Route {formatWorkflowToken(entry.routing_policy_id ?? "default")} · {entry.routing_targets.length
                      ? entry.routing_targets.join(", ")
                      : "no targets"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Escalations {entry.escalation_count}
                  </p>
                </td>
                <td>
                  <strong>{formatWorkflowToken(entry.last_delivery_status ?? "not_escalated")}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.last_delivery_summary ?? "Not escalated yet."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Approval {formatWorkflowToken(entry.approval_state)} · {entry.approval_summary ?? "No approval summary recorded."}
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
      ) : null}
      {selectedProviderProvenanceSchedulerExportJobId ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Scheduler export audit trail</strong>
            <p>{shortenIdentifier(selectedProviderProvenanceSchedulerExportJobId, 10)}</p>
          </div>
          {selectedProviderProvenanceSchedulerExportEntry ? (
            <div className="provider-provenance-workspace-card">
              <div className="market-data-provenance-history-head">
                <strong>Escalation policy</strong>
                <p>
                  Save a per-export routing policy, require approval when needed, and then
                  escalate the selected scheduler snapshot.
                </p>
              </div>
              <div className="filter-bar">
                <label>
                  <span>Route</span>
                  <select
                    onChange={(event) =>
                      setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                        ...current,
                        routing_policy_id: event.target.value,
                        delivery_targets:
                          event.target.value === "custom"
                            ? (
                              current.delivery_targets.length
                                ? current.delivery_targets
                                : [...selectedProviderProvenanceSchedulerExportEntry.available_delivery_targets]
                            )
                            : current.delivery_targets,
                      }))
                    }
                    value={providerProvenanceSchedulerExportPolicyDraft.routing_policy_id}
                  >
                    <option value="default">Default recommendation</option>
                    <option value="chatops_only">Chatops only</option>
                    <option value="all_targets">All targets</option>
                    <option value="paging_only">Paging only</option>
                    <option value="custom">Custom targets</option>
                  </select>
                </label>
                <label>
                  <span>Approval</span>
                  <select
                    onChange={(event) =>
                      setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                        ...current,
                        approval_policy_id: event.target.value === "manual_required"
                          ? "manual_required"
                          : "auto",
                      }))
                    }
                    value={providerProvenanceSchedulerExportPolicyDraft.approval_policy_id}
                  >
                    <option value="auto">Auto</option>
                    <option value="manual_required">Manual approval required</option>
                  </select>
                </label>
                <label>
                  <span>Approval note</span>
                  <input
                    onChange={(event) =>
                      setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                        ...current,
                        approval_note: event.target.value,
                      }))
                    }
                    placeholder="manager_review_complete"
                    type="text"
                    value={providerProvenanceSchedulerExportPolicyDraft.approval_note}
                  />
                </label>
              </div>
              {providerProvenanceSchedulerExportPolicyDraft.routing_policy_id === "custom" ? (
                <div className="filter-bar">
                  {selectedProviderProvenanceSchedulerExportEntry.available_delivery_targets.map((target) => (
                    <label className="provider-provenance-checkbox" key={`provider-scheduler-target-${target}`}>
                      <input
                        checked={providerProvenanceSchedulerExportPolicyDraft.delivery_targets.includes(target)}
                        onChange={(event) =>
                          setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                            ...current,
                            delivery_targets: event.target.checked
                              ? Array.from(new Set([...current.delivery_targets, target]))
                              : current.delivery_targets.filter((candidate) => candidate !== target),
                          }))
                        }
                        type="checkbox"
                      />
                      <span>{target}</span>
                    </label>
                  ))}
                </div>
              ) : null}
              <div className="run-filter-summary-chip-row">
                <span className="run-filter-summary-chip">
                  Current route {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.routing_policy_id ?? "default")}
                </span>
                <span className="run-filter-summary-chip">
                  Targets {selectedProviderProvenanceSchedulerExportEntry.routing_targets.length
                    ? selectedProviderProvenanceSchedulerExportEntry.routing_targets.join(", ")
                    : "none"}
                </span>
                <span className="run-filter-summary-chip">
                  Approval {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.approval_state)}
                </span>
                {selectedProviderProvenanceSchedulerExportEntry.approved_at ? (
                  <span className="run-filter-summary-chip">
                    Approved {formatTimestamp(selectedProviderProvenanceSchedulerExportEntry.approved_at)} by {selectedProviderProvenanceSchedulerExportEntry.approved_by ?? "unknown"}
                  </span>
                ) : null}
              </div>
              <p className="market-data-workflow-export-copy">
                {selectedProviderProvenanceSchedulerExportEntry.routing_policy_summary ?? "No routing summary recorded."}{" "}
                {selectedProviderProvenanceSchedulerExportEntry.approval_summary ?? "No approval summary recorded."}
              </p>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  onClick={() => {
                    void updateSharedProviderProvenanceSchedulerExportPolicy(
                      selectedProviderProvenanceSchedulerExportEntry,
                    );
                  }}
                  type="button"
                >
                  Save policy
                </button>
                <button
                  className="ghost-button"
                  disabled={
                    !selectedProviderProvenanceSchedulerExportEntry.approval_required
                    || selectedProviderProvenanceSchedulerExportEntry.approval_state === "approved"
                  }
                  onClick={() => {
                    void approveSharedProviderProvenanceSchedulerExport(
                      selectedProviderProvenanceSchedulerExportEntry,
                    );
                  }}
                  type="button"
                >
                  Approve route
                </button>
                <button
                  className="ghost-button"
                  disabled={
                    selectedProviderProvenanceSchedulerExportEntry.approval_required
                    && selectedProviderProvenanceSchedulerExportEntry.approval_state !== "approved"
                  }
                  onClick={() => {
                    void escalateSharedProviderProvenanceSchedulerExport(
                      selectedProviderProvenanceSchedulerExportEntry,
                    );
                  }}
                  type="button"
                >
                  Escalate now
                </button>
              </div>
            </div>
          ) : null}
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
                      <strong>{record.source_tab_label ?? record.requested_by_tab_label ?? "unknown tab"}</strong>
                      <p className="run-lineage-symbol-copy">
                        {record.source_tab_id ?? record.requested_by_tab_id ?? "No tab id recorded."}
                      </p>
                    </td>
                    <td>
                      <strong>{record.detail}</strong>
                      <p className="run-lineage-symbol-copy">
                        Route {formatWorkflowToken(record.routing_policy_id ?? "default")} · {record.routing_targets.length
                          ? record.routing_targets.join(", ")
                          : "no routing targets recorded"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Approval {record.approval_state
                          ? formatWorkflowToken(record.approval_state)
                          : "not recorded"} · {record.approval_summary ?? "No approval summary recorded."}
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
          ) : selectedProviderProvenanceSchedulerExportHistory && !providerProvenanceSchedulerExportHistoryLoading ? (
            <p className="empty-state">No scheduler export audit events recorded yet.</p>
          ) : null}
        </div>
      ) : null}
    </>
  );
}
