// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeTemplateId ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Template revision history</strong>
        <p>Inspect immutable snapshots, apply them to the workbench, or restore them as the active template.</p>
      </div>
      {providerProvenanceSchedulerNarrativeTemplateHistoryLoading ? (
        <p className="empty-state">Loading template revisions…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplateHistoryError ? (
        <p className="market-data-workflow-feedback">
          Template revision history failed: {providerProvenanceSchedulerNarrativeTemplateHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeTemplateHistory ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Snapshot</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {selectedProviderProvenanceSchedulerNarrativeTemplateHistory.history.map((entry) => (
              <tr key={entry.revision_id}>
                <td>
                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                  <p className="run-lineage-symbol-copy">{entry.reason}</p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void applyProviderProvenanceWorkspaceQuery(entry, {
                          includeLayout: false,
                          forceSchedulerHighlight: true,
                          feedbackLabel: `Template revision ${entry.revision_id}`,
                        });
                      }}
                      type="button"
                    >
                      Apply snapshot
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void restoreProviderProvenanceSchedulerNarrativeTemplateHistoryRevision(entry);
                      }}
                      type="button"
                    >
                      Restore revision
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </div>
  ) : null;
}
