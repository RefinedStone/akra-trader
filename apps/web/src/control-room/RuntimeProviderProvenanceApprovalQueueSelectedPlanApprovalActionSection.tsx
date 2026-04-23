// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueSelectedPlanApprovalActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-actions">
      <button
        className="ghost-button"
        disabled={
          selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "previewed"
          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
        }
        onClick={() => {
          void approveProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
        }}
        type="button"
      >
        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
          ? "Approving…"
          : "Approve plan"}
      </button>
      <button
        className="ghost-button"
        disabled={
          selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "approved"
          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
        }
        onClick={() => {
          void applyProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
        }}
        type="button"
      >
        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
          ? "Applying…"
          : "Apply approved plan"}
      </button>
      <button
        className="ghost-button"
        disabled={
          selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "applied"
          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
        }
        onClick={() => {
          void rollbackProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
        }}
        type="button"
      >
        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
          ? "Rolling back…"
          : "Rollback plan"}
      </button>
    </div>
  );
}
