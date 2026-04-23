// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueAsyncStateSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading ? (
        <p className="empty-state">Loading stitched governance registry approval queue…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError ? (
        <p className="market-data-workflow-feedback">
          Stitched governance registry approval queue failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError}
        </p>
      ) : null}
    </>
  );
}
