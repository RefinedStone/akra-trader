// @ts-nocheck
export function RuntimeProviderProvenanceFocusedIngestionJobsSection({ model }: { model: any }) {
  const {
    marketDataIngestionJobs,
    formatTimestamp,
    formatWorkflowToken,
    formatRange,
    truncateLabel,
  } = model;

  return (
    <div>
      <h3>Ingestion jobs (수집 작업)</h3>
      {marketDataIngestionJobs.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>완료 시각</th>
              <th>Status</th>
              <th>Operation</th>
              <th>수집 수</th>
              <th>상세</th>
            </tr>
          </thead>
          <tbody>
            {marketDataIngestionJobs.slice(0, 6).map((job) => (
              <tr key={job.job_id}>
                <td>{formatTimestamp(job.finished_at)}</td>
                <td>{job.status}</td>
                <td>{job.operation}</td>
                <td>{job.fetched_candle_count}</td>
                <td>
                  <strong>{job.duration_ms} ms</strong>
                  <p className="run-lineage-symbol-copy">
                    Claim: {formatWorkflowToken(job.validation_claim)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    요청 구간: {formatRange(job.requested_start_at, job.requested_end_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {job.last_error ? truncateLabel(job.last_error, 84) : "기록된 Job error가 없습니다."}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">이 focus에 기록된 Ingestion job이 없습니다.</p>
      )}
    </div>
  );
}
