// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAutomationDailyTrendsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (!providerProvenanceSchedulerAnalytics) {
    return null;
  }

  return (
    <div className="status-grid-two-column market-data-provenance-time-series-grid">
      <div className="market-data-provenance-time-series-panel">
        <div className="market-data-provenance-history-head">
          <strong>Health status by day</strong>
          <p>Daily scheduler-cycle mix across the current provenance automation window.</p>
        </div>
        <div className="run-filter-summary-chip-row">
          <span className="run-filter-summary-chip">
            Peak cycle day{" "}
            {providerProvenanceSchedulerAnalytics.time_series.health_status.summary
              .peak_cycle_bucket_label ?? "n/a"}{" "}
            ·{" "}
            {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.peak_cycle_count}{" "}
            cycle(s)
          </span>
          <span className="run-filter-summary-chip">
            Latest{" "}
            {providerProvenanceSchedulerAnalytics.time_series.health_status.summary
              .latest_bucket_label ?? "n/a"}{" "}
            ·{" "}
            {formatWorkflowToken(
              providerProvenanceSchedulerAnalytics.time_series.health_status.summary.latest_status,
            )}
          </span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Cycles</th>
              <th>Status mix</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerAnalytics.time_series.health_status.series.map((bucket) => (
              <tr key={`provider-scheduler-health-${bucket.bucket_key}`}>
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
                  <strong>{formatWorkflowToken(bucket.dominant_status)}</strong>
                  <p className="run-lineage-symbol-copy">
                    Healthy {bucket.healthy_count} · lagging {bucket.lagging_count} · failed{" "}
                    {bucket.failed_count}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {bucket.latest_summary || "No scheduler events recorded."}
                  </p>
                </td>
                <td>
                  <button
                    className="ghost-button"
                    onClick={() => {
                      setProviderProvenanceSchedulerDrilldownBucketKey(bucket.bucket_key);
                    }}
                    type="button"
                  >
                    {providerProvenanceSchedulerDrilldownBucketKey === bucket.bucket_key
                      ? "Selected"
                      : "Hour view"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="market-data-provenance-time-series-panel">
        <div className="market-data-provenance-history-head">
          <strong>Lag and backlog trend</strong>
          <p>Daily peak lag, due backlog, and failure pressure for scheduler cycles.</p>
        </div>
        <div className="run-filter-summary-chip-row">
          <span className="run-filter-summary-chip">
            Peak lag{" "}
            {providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary
              .peak_lag_bucket_label ?? "n/a"}{" "}
            ·{" "}
            {formatSchedulerLagSeconds(
              providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.peak_lag_seconds,
            )}
          </span>
          <span className="run-filter-summary-chip">
            Latest lag{" "}
            {formatSchedulerLagSeconds(
              providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.latest_lag_seconds,
            )}{" "}
            ·{" "}
            {providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary
              .latest_due_report_count}{" "}
            due
          </span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Lag</th>
              <th>Backlog</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerAnalytics.time_series.lag_trend.series.map((bucket) => (
              <tr key={`provider-scheduler-lag-${bucket.bucket_key}`}>
                <td>
                  <strong>{bucket.bucket_label}</strong>
                  <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                </td>
                <td>
                  <strong>{formatSchedulerLagSeconds(bucket.peak_lag_seconds)}</strong>
                  <div className="market-data-provenance-timeseries-track">
                    <div
                      className="market-data-provenance-timeseries-bar is-warning"
                      style={{
                        width: resolveProviderProvenanceSeriesBarWidth(
                          bucket.peak_lag_seconds,
                          providerProvenanceSchedulerLagBarMax,
                        ),
                      }}
                    />
                  </div>
                  <p className="run-lineage-symbol-copy">
                    Latest {formatSchedulerLagSeconds(bucket.latest_lag_seconds)} · avg{" "}
                    {formatSchedulerLagSeconds(bucket.average_lag_seconds)}
                  </p>
                </td>
                <td>
                  <strong>{bucket.peak_due_report_count} due report(s)</strong>
                  <p className="run-lineage-symbol-copy">
                    Failures {bucket.failure_count} · executed {bucket.executed_report_count}
                  </p>
                </td>
                <td>
                  <button
                    className="ghost-button"
                    onClick={() => {
                      setProviderProvenanceSchedulerDrilldownBucketKey(
                        bucket.bucket_key.slice(0, 10),
                      );
                    }}
                    type="button"
                  >
                    {providerProvenanceSchedulerDrilldownBucketKey === bucket.bucket_key.slice(0, 10)
                      ? "Selected"
                      : "Hour view"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
