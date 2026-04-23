// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueActionSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            reviewProviderProvenanceSchedulerStitchedReportGovernanceRegistryPlanInSharedQueue(plan);
          }}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
            ? "Shared queue selected"
            : "Review in shared queue"}
        </button>
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
      </div>
    </td>
  );
}
