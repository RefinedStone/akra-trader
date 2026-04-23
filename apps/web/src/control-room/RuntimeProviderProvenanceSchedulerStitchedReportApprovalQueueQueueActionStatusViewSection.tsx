// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionStatusViewSection({
  model,
  plan,
  onClick,
}: {
  model: any;
  plan: any;
  onClick: () => void;
}) {
  const { selectedProviderProvenanceSchedulerNarrativeGovernancePlanId } = model;

  return (
    <button
      className="ghost-button"
      onClick={onClick}
      type="button"
    >
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
        ? "Shared queue selected"
        : "Review in shared queue"}
    </button>
  );
}
