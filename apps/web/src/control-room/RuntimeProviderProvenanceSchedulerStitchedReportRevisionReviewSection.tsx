// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportRevisionReviewSection({ model }: { model: any }) {
  const {} = model;

  return selectedProviderProvenanceSchedulerStitchedReportViewId ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Stitched report view revisions</strong>
        <p>
          Inspect immutable saved-view snapshots, apply them to the workbench, or restore them
          as the active stitched report view.
        </p>
      </div>
      {providerProvenanceSchedulerStitchedReportViewHistoryLoading ? (
        <p className="empty-state">Loading stitched report view revisions…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViewHistoryError ? (
        <p className="market-data-workflow-feedback">
          Stitched report view revisions failed:{" "}
          {providerProvenanceSchedulerStitchedReportViewHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerStitchedReportViewHistory ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Snapshot</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {selectedProviderProvenanceSchedulerStitchedReportViewHistory.history.map((entry) => (
              <tr key={entry.revision_id}>
                <td>
                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <strong>
                    {formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}
                  </strong>
                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                  <p className="run-lineage-symbol-copy">
                    {entry.occurrence_limit} occurrence(s) · history {entry.history_limit} ·
                    drill-down {entry.drilldown_history_limit}
                  </p>
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
                          feedbackLabel: `Stitched report revision ${entry.revision_id}`,
                        });
                      }}
                      type="button"
                    >
                      Apply snapshot
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void restoreProviderProvenanceSchedulerStitchedReportViewHistoryRevision(
                          entry,
                        );
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
