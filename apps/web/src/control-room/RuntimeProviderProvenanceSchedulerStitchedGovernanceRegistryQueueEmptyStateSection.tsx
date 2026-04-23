// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueEmptyStateSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return !providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading ? (
    <p className="empty-state">No stitched governance registry plans match the dedicated queue filters.</p>
  ) : null;
}
