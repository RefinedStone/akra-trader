// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerWorkspaceAsyncStateSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerAnalyticsLoading && !providerProvenanceSchedulerAnalytics ? (
        <p className="empty-state">Loading scheduler automation trends…</p>
      ) : null}
      {providerProvenanceSchedulerAnalyticsError ? (
        <p className="market-data-workflow-feedback">
          Scheduler automation analytics failed: {providerProvenanceSchedulerAnalyticsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerHistoryError ? (
        <p className="market-data-workflow-feedback">
          Scheduler automation history failed: {providerProvenanceSchedulerHistoryError}
        </p>
      ) : null}
    </>
  );
}
