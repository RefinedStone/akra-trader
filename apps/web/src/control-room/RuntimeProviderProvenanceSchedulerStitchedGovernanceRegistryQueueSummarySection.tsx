// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSummarySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-governance-summary">
      <strong>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.total} registry plan(s)
      </strong>
      <span>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.pending_approval_count} pending approval · {" "}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.ready_to_apply_count} ready to apply · {" "}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.completed_count} completed
      </span>
    </div>
  );
}
