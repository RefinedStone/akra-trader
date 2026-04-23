// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeRegistryId ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Registry revision history</strong>
        <p>Review saved board revisions, apply them to the workbench, or restore them as the active shared scheduler board.</p>
      </div>
      {providerProvenanceSchedulerNarrativeRegistryHistoryLoading ? (
        <p className="empty-state">Loading registry revisions…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeRegistryHistoryError ? (
        <p className="market-data-workflow-feedback">
          Registry revision history failed: {providerProvenanceSchedulerNarrativeRegistryHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeRegistryHistory ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Snapshot</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {selectedProviderProvenanceSchedulerNarrativeRegistryHistory.history.map((entry) => (
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
                  <p className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerNarrativeTemplateNameMap.get(entry.template_id ?? "") ?? "No template link"} · highlight {entry.layout.highlight_panel}
                  </p>
                  <p className="run-lineage-symbol-copy">{entry.reason}</p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void applyProviderProvenanceWorkspaceQuery(entry, {
                          includeLayout: true,
                          feedbackLabel: `Registry revision ${entry.revision_id}`,
                        });
                      }}
                      type="button"
                    >
                      Apply snapshot
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void restoreProviderProvenanceSchedulerNarrativeRegistryHistoryRevision(entry);
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
