// @ts-nocheck
export function RuntimeProviderProvenanceFocusedLineageIncidentHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div>
      <h3>Lineage incident history</h3>
      {focusedMarketIncidentHistory.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Source</th>
              <th>Signal</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {focusedMarketIncidentHistory.map((entry) => (
              <tr key={entry.entryId}>
                <td>{formatTimestamp(entry.occurredAt)}</td>
                <td>
                  <span className={`market-data-incident-badge is-${entry.tone}`.trim()}>
                    {entry.sourceLabel}
                  </span>
                </td>
                <td>{entry.statusLabel}</td>
                <td>
                  <strong>{entry.summary}</strong>
                  <p className="run-lineage-symbol-copy">{entry.detail}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">
          No alert-linked lineage incident history recorded for this focus.
        </p>
      )}
    </div>
  );
}
