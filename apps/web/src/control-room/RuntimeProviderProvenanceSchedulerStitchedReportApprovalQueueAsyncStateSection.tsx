// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportGovernancePlansLoading ? (
        <p className="empty-state">Loading stitched report approval queue…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportGovernancePlansError ? (
        <p className="market-data-workflow-feedback">
          Stitched report approval queue failed: {providerProvenanceSchedulerStitchedReportGovernancePlansError}
        </p>
      ) : null}
    </>
  );
}
