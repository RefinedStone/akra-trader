// @ts-nocheck
export function RuntimeProviderProvenanceFocusedLineageHistorySection({ model }: { model: any }) {
  const {
    marketDataLineageHistory,
    formatTimestamp,
    formatWorkflowToken,
    shortenIdentifier,
    formatRange,
  } = model;

  return (
    <div>
      <h3>Lineage history (동기화 근거)</h3>
      {marketDataLineageHistory.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>기록 시각</th>
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
                    24시간 실패 {record.failure_count_24h}건
                    {record.gap_window_count ? ` · Gap ${record.gap_window_count}개` : ""}
                  </strong>
                  <p className="run-lineage-symbol-copy">
                    {record.issues.length ? record.issues.join(", ") : "기록된 Lineage 이슈가 없습니다."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Window: {formatRange(record.first_timestamp, record.last_timestamp)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Checkpoint: {record.checkpoint_id ? shortenIdentifier(record.checkpoint_id, 22) : "없음"}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">이 focus에 기록된 Lineage 이력이 없습니다.</p>
      )}
    </div>
  );
}
