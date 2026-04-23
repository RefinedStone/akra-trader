// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAutomationSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Scheduler automation</strong>
        <p>
          Persisted health history and daily trend buckets for provenance report
          automation.
        </p>
      </div>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            void copyProviderProvenanceSchedulerHealthJsonExport();
          }}
          type="button"
        >
          Copy JSON export
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void shareProviderProvenanceSchedulerHealthExport();
          }}
          type="button"
        >
          Share export
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void downloadProviderProvenanceSchedulerHealthCsv();
          }}
          type="button"
        >
          Download CSV page
        </button>
        {providerProvenanceSchedulerDrilldownBucketKey ? (
          <button
            className="ghost-button"
            onClick={() => {
              setProviderProvenanceSchedulerDrilldownBucketKey(null);
            }}
            type="button"
          >
            Reset drill-down
          </button>
        ) : null}
      </div>
      <div className="status-grid">
        <div className="metric-tile">
          <span>Current status</span>
          <strong>{formatWorkflowToken(providerProvenanceSchedulerCurrent.status)}</strong>
        </div>
        <div className="metric-tile">
          <span>Due backlog</span>
          <strong>{providerProvenanceSchedulerCurrent.due_report_count}</strong>
        </div>
        <div className="metric-tile">
          <span>Peak lag</span>
          <strong>{formatSchedulerLagSeconds(providerProvenanceSchedulerCurrent.max_due_lag_seconds)}</strong>
        </div>
        <div className="metric-tile">
          <span>Total executed</span>
          <strong>{providerProvenanceSchedulerCurrent.total_executed_count}</strong>
        </div>
        <div className="metric-tile">
          <span>Success / failure</span>
          <strong>
            {providerProvenanceSchedulerCurrent.success_count} / {providerProvenanceSchedulerCurrent.failure_count}
          </strong>
        </div>
        <div className="metric-tile">
          <span>Last success</span>
          <strong>{formatTimestamp(providerProvenanceSchedulerCurrent.last_success_at)}</strong>
        </div>
      </div>
      <p className="market-data-workflow-export-copy">
        {providerProvenanceSchedulerCurrent.summary}
      </p>
      <div className="run-filter-summary-chip-row">
        <span className="run-filter-summary-chip">
          Interval {providerProvenanceSchedulerCurrent.interval_seconds}s · batch {providerProvenanceSchedulerCurrent.batch_limit}
        </span>
        <span className="run-filter-summary-chip">
          Last cycle {formatTimestamp(providerProvenanceSchedulerCurrent.last_cycle_finished_at)}
        </span>
        {providerProvenanceSchedulerCurrent.oldest_due_at ? (
          <span className="run-filter-summary-chip">
            Oldest due {formatTimestamp(providerProvenanceSchedulerCurrent.oldest_due_at)}
          </span>
        ) : null}
        {providerProvenanceSchedulerCurrent.last_error ? (
          <span className="run-filter-summary-chip">
            Last error {providerProvenanceSchedulerCurrent.last_error}
          </span>
        ) : null}
        {providerProvenanceSchedulerCurrent.issues.map((issue) => (
          <span className="run-filter-summary-chip" key={`provider-scheduler-issue-${issue}`}>
            {issue}
          </span>
        ))}
      </div>
      {providerProvenanceSchedulerAnalytics ? (
        <div className="status-grid-two-column market-data-provenance-time-series-grid">
          <div className="market-data-provenance-time-series-panel">
            <div className="market-data-provenance-history-head">
              <strong>Health status by day</strong>
              <p>
                Daily scheduler-cycle mix across the current provenance automation window.
              </p>
            </div>
            <div className="run-filter-summary-chip-row">
              <span className="run-filter-summary-chip">
                Peak cycle day {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.peak_cycle_bucket_label ?? "n/a"} · {" "}
                {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.peak_cycle_count} cycle(s)
              </span>
              <span className="run-filter-summary-chip">
                Latest {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.latest_bucket_label ?? "n/a"} · {" "}
                {formatWorkflowToken(providerProvenanceSchedulerAnalytics.time_series.health_status.summary.latest_status)}
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
                        Healthy {bucket.healthy_count} · lagging {bucket.lagging_count} · failed {bucket.failed_count}
                      </p>
                      <p className="run-lineage-symbol-copy">{bucket.latest_summary || "No scheduler events recorded."}</p>
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
              <p>
                Daily peak lag, due backlog, and failure pressure for scheduler cycles.
              </p>
            </div>
            <div className="run-filter-summary-chip-row">
              <span className="run-filter-summary-chip">
                Peak lag {providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.peak_lag_bucket_label ?? "n/a"} · {" "}
                {formatSchedulerLagSeconds(providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.peak_lag_seconds)}
              </span>
              <span className="run-filter-summary-chip">
                Latest lag {formatSchedulerLagSeconds(providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.latest_lag_seconds)} · {" "}
                {providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.latest_due_report_count} due
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
                        Latest {formatSchedulerLagSeconds(bucket.latest_lag_seconds)} · avg {formatSchedulerLagSeconds(bucket.average_lag_seconds)}
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
      ) : null}
      {providerProvenanceSchedulerDrillDown ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Hourly drill-down · {providerProvenanceSchedulerDrillDown.bucket_label}</strong>
            <p>
              Review hour-level scheduler pressure and the raw cycle records for the
              selected day bucket.
            </p>
          </div>
          <div className="run-filter-summary-chip-row">
            <span className="run-filter-summary-chip">
              {providerProvenanceSchedulerDrillDown.total_record_count} recorded cycle(s)
            </span>
            <span className="run-filter-summary-chip">
              Peak lag {formatSchedulerLagSeconds(providerProvenanceSchedulerDrillDown.lag_trend.summary.peak_lag_seconds)}
            </span>
            <span className="run-filter-summary-chip">
              Latest {formatWorkflowToken(providerProvenanceSchedulerDrillDown.health_status.summary.latest_status)}
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
                          Healthy {bucket.healthy_count} · lagging {bucket.lagging_count} · failed {bucket.failed_count}
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
                          Latest {formatSchedulerLagSeconds(bucket.latest_lag_seconds)} · avg {formatSchedulerLagSeconds(bucket.average_lag_seconds)}
                        </p>
                      </td>
                      <td>
                        <strong>{bucket.peak_due_report_count} due</strong>
                        <p className="run-lineage-symbol-copy">
                          Failures {bucket.failure_count}
                        </p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="market-data-provenance-history-head">
            <strong>Selected-day cycle records</strong>
            <p>
              The most recent recorded scheduler cycles inside the selected day bucket.
            </p>
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
                        Lag {formatSchedulerLagSeconds(entry.max_due_lag_seconds)} · due {entry.due_report_count}
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
      ) : null}
      <div className="market-data-provenance-history-head">
        <strong>Recent scheduler cycles</strong>
        <p>
          Review the persisted automation history that backs the trend surfaces.
        </p>
      </div>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={!providerProvenanceSchedulerHistory?.previous_offset && providerProvenanceSchedulerHistoryOffset === 0}
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
                    Lag {formatSchedulerLagSeconds(entry.max_due_lag_seconds)} · due {entry.due_report_count}
                  </p>
                </td>
                <td>
                  <strong>{entry.summary}</strong>
                  <p className="run-lineage-symbol-copy">
                    Executed {entry.last_executed_count} report(s) · cycle {entry.cycle_count}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.last_error ?? (entry.issues.join(" · ") || "No blocking issues recorded.")}
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
