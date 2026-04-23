// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAutomationDrillDownSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (!providerProvenanceSchedulerDrillDown) {
    return null;
  }

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Hourly drill-down · {providerProvenanceSchedulerDrillDown.bucket_label}</strong>
        <p>
          Review hour-level scheduler pressure and the raw cycle records for the selected day
          bucket.
        </p>
      </div>
      <div className="run-filter-summary-chip-row">
        <span className="run-filter-summary-chip">
          {providerProvenanceSchedulerDrillDown.total_record_count} recorded cycle(s)
        </span>
        <span className="run-filter-summary-chip">
          Peak lag{" "}
          {formatSchedulerLagSeconds(
            providerProvenanceSchedulerDrillDown.lag_trend.summary.peak_lag_seconds,
          )}
        </span>
        <span className="run-filter-summary-chip">
          Latest{" "}
          {formatWorkflowToken(
            providerProvenanceSchedulerDrillDown.health_status.summary.latest_status,
          )}
        </span>
      </div>
      <div className="status-grid-two-column market-data-provenance-time-series-grid">
        <div className="market-data-provenance-time-series-panel">
          <div className="market-data-provenance-history-head">
            <strong>Status by hour</strong>
            <p>Hour-level cycle mix for the selected day bucket.</p>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Hour</th>
                <th>Cycles</th>
                <th>Status mix</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerDrillDown.health_status.series.map((bucket) => (
                <tr key={`provider-scheduler-hour-health-${bucket.bucket_key}`}>
                  <td>
                    <strong>{bucket.bucket_label}</strong>
                    <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                  </td>
                  <td>
                    <strong>{bucket.cycle_count} cycle(s)</strong>
                    <p className="run-lineage-symbol-copy">
                      Executed {bucket.executed_report_count} report(s)
                    </p>
                  </td>
                  <td>
                    <strong>{formatWorkflowToken(bucket.latest_status)}</strong>
                    <p className="run-lineage-symbol-copy">
                      Healthy {bucket.healthy_count} · lagging {bucket.lagging_count} · failed{" "}
                      {bucket.failed_count}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="market-data-provenance-time-series-panel">
          <div className="market-data-provenance-history-head">
            <strong>Lag by hour</strong>
            <p>Peak and latest lag inside the selected scheduler day bucket.</p>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Hour</th>
                <th>Lag</th>
                <th>Backlog</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerDrillDown.lag_trend.series.map((bucket) => (
                <tr key={`provider-scheduler-hour-lag-${bucket.bucket_key}`}>
                  <td>
                    <strong>{bucket.bucket_label}</strong>
                    <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                  </td>
                  <td>
                    <strong>{formatSchedulerLagSeconds(bucket.peak_lag_seconds)}</strong>
                    <p className="run-lineage-symbol-copy">
                      Latest {formatSchedulerLagSeconds(bucket.latest_lag_seconds)} · avg{" "}
                      {formatSchedulerLagSeconds(bucket.average_lag_seconds)}
                    </p>
                  </td>
                  <td>
                    <strong>{bucket.peak_due_report_count} due</strong>
                    <p className="run-lineage-symbol-copy">Failures {bucket.failure_count}</p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="market-data-provenance-history-head">
        <strong>Selected-day cycle records</strong>
        <p>The most recent recorded scheduler cycles inside the selected day bucket.</p>
      </div>
      {providerProvenanceSchedulerDrillDown.history.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Recorded</th>
              <th>Status</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerDrillDown.history.map((entry) => (
              <tr key={`provider-scheduler-drill-history-${entry.record_id}`}>
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
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No hourly scheduler records were captured for the selected day.</p>
      )}
    </div>
  );
}
