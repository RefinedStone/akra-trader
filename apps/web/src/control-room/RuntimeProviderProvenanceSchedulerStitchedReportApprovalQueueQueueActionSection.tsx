// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <button
      className="ghost-button"
      onClick={() => {
        reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue(plan);
      }}
      type="button"
    >
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
        ? "Shared queue selected"
        : "Review in shared queue"}
    </button>
  );
}
