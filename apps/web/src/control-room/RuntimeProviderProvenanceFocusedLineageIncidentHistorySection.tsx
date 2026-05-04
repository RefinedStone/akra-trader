// @ts-nocheck
export function RuntimeProviderProvenanceFocusedLineageIncidentHistorySection({
  model,
}: {
  model: any;
}) {
  const { focusedMarketIncidentHistory, formatTimestamp } = model;

  return (
    <div>
      <h3>Lineage incident history (이슈 이력)</h3>
      {focusedMarketIncidentHistory.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>시각</th>
              <th>출처</th>
              <th>Signal</th>
              <th>상세</th>
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
          이 focus에 연결된 Alert/Incident 이력이 없습니다.
        </p>
      )}
    </div>
  );
}
