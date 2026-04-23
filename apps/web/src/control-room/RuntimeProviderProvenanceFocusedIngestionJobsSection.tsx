// @ts-nocheck
export function RuntimeProviderProvenanceFocusedIngestionJobsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div>
      <h3>Ingestion jobs</h3>
      {marketDataIngestionJobs.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Finished</th>
              <th>Status</th>
              <th>Operation</th>
              <th>Fetched</th>
              <th>Detail</th>
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
                    Requested: {formatRange(job.requested_start_at, job.requested_end_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {job.last_error ? truncateLabel(job.last_error, 84) : "No job error recorded."}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No ingestion jobs recorded for this focus.</p>
      )}
    </div>
  );
}
