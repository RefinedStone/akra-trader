// @ts-nocheck
export function RuntimeProviderProvenanceFocusedLineageHistorySection({ model }: { model: any }) {
  const {} = model;

  return (
    <div>
      <h3>Lineage history</h3>
      {marketDataLineageHistory.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Recorded</th>
              <th>Sync</th>
              <th>Claim</th>
              <th>Boundary</th>
              <th>Signal</th>
            </tr>
          </thead>
          <tbody>
            {marketDataLineageHistory.slice(0, 6).map((record) => (
              <tr key={record.history_id}>
                <td>{formatTimestamp(record.recorded_at)}</td>
                <td>{record.sync_status}</td>
                <td>{formatWorkflowToken(record.validation_claim)}</td>
                <td title={record.boundary_id ?? undefined}>
                  {record.boundary_id ? shortenIdentifier(record.boundary_id, 22) : "n/a"}
                </td>
                <td>
                  <strong>
                    {record.failure_count_24h} failures / 24h
                    {record.gap_window_count ? ` · ${record.gap_window_count} gaps` : ""}
                  </strong>
                  <p className="run-lineage-symbol-copy">
                    {record.issues.length ? record.issues.join(", ") : "No lineage issues recorded."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Window: {formatRange(record.first_timestamp, record.last_timestamp)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Checkpoint: {record.checkpoint_id ? shortenIdentifier(record.checkpoint_id, 22) : "n/a"}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No lineage history recorded for this focus.</p>
      )}
    </div>
  );
}
