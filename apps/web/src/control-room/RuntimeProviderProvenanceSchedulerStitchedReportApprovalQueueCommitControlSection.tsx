// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitControlSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <>
      <button
        className="ghost-button"
        disabled={
          plan.status !== "previewed"
          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
        }
        onClick={() => {
          void approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
        }}
        type="button"
      >
        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
          ? "Approving…"
          : "Approve"}
      </button>
      <button
        className="ghost-button"
        disabled={
          plan.status !== "approved"
          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
        }
        onClick={() => {
          void applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
        }}
        type="button"
      >
        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
          ? "Applying…"
          : "Apply"}
      </button>
      <button
        className="ghost-button"
        disabled={
          plan.status !== "applied"
          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
        }
        onClick={() => {
          void rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
        }}
        type="button"
      >
        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
          ? "Rolling back…"
          : "Rollback"}
      </button>
    </>
  );
}
