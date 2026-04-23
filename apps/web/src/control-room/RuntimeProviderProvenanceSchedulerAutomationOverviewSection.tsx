// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAutomationOverviewSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Scheduler automation</strong>
        <p>Persisted health history and daily trend buckets for provenance report automation.</p>
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
          <strong>
            {formatSchedulerLagSeconds(providerProvenanceSchedulerCurrent.max_due_lag_seconds)}
          </strong>
        </div>
        <div className="metric-tile">
          <span>Total executed</span>
          <strong>{providerProvenanceSchedulerCurrent.total_executed_count}</strong>
        </div>
        <div className="metric-tile">
          <span>Success / failure</span>
          <strong>
            {providerProvenanceSchedulerCurrent.success_count} /{" "}
            {providerProvenanceSchedulerCurrent.failure_count}
          </strong>
        </div>
        <div className="metric-tile">
          <span>Last success</span>
          <strong>{formatTimestamp(providerProvenanceSchedulerCurrent.last_success_at)}</strong>
        </div>
      </div>
      <p className="market-data-workflow-export-copy">{providerProvenanceSchedulerCurrent.summary}</p>
      <div className="run-filter-summary-chip-row">
        <span className="run-filter-summary-chip">
          Interval {providerProvenanceSchedulerCurrent.interval_seconds}s · batch{" "}
          {providerProvenanceSchedulerCurrent.batch_limit}
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
    </>
  );
}
