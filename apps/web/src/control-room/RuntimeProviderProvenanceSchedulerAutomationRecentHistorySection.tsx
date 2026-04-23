// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAutomationRecentHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Recent scheduler cycles</strong>
        <p>Review the persisted automation history that backs the trend surfaces.</p>
      </div>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={
            !providerProvenanceSchedulerHistory?.previous_offset &&
            providerProvenanceSchedulerHistoryOffset === 0
          }
          onClick={() => {
            setProviderProvenanceSchedulerHistoryOffset(
              providerProvenanceSchedulerHistory?.previous_offset ?? 0,
            );
          }}
          type="button"
        >
          Previous page
        </button>
        <button
          className="ghost-button"
          disabled={!(providerProvenanceSchedulerHistory?.has_more ?? false)}
          onClick={() => {
            if (typeof providerProvenanceSchedulerHistory?.next_offset === "number") {
              setProviderProvenanceSchedulerHistoryOffset(
                providerProvenanceSchedulerHistory.next_offset,
              );
            }
          }}
          type="button"
        >
          Next page
        </button>
        <span className="run-lineage-symbol-copy">
          {providerProvenanceSchedulerHistory
            ? `${providerProvenanceSchedulerHistory.query.offset + 1}-${providerProvenanceSchedulerHistory.query.offset + providerProvenanceSchedulerHistory.returned} of ${providerProvenanceSchedulerHistory.total}`
            : "Page 1"}
        </span>
      </div>
      {providerProvenanceSchedulerHistoryLoading && !providerProvenanceSchedulerRecentHistory.length ? (
        <p className="empty-state">Loading scheduler cycle history…</p>
      ) : null}
      {providerProvenanceSchedulerRecentHistory.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Recorded</th>
              <th>Status</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerRecentHistory.map((entry) => (
              <tr key={entry.record_id}>
                <td>
                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.source_tab_label ?? entry.source_tab_id ?? "scheduler"}
                  </p>
                </td>
                <td>
                  <strong>{formatWorkflowToken(entry.status)}</strong>
                  <p className="run-lineage-symbol-copy">
                    Lag {formatSchedulerLagSeconds(entry.max_due_lag_seconds)} · due{" "}
                    {entry.due_report_count}
                  </p>
                </td>
                <td>
                  <strong>{entry.summary}</strong>
                  <p className="run-lineage-symbol-copy">
                    Executed {entry.last_executed_count} report(s) · cycle {entry.cycle_count}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.last_error ??
                      (entry.issues.join(" · ") || "No blocking issues recorded.")}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No scheduler cycle history recorded yet.</p>
      )}
    </>
  );
}
