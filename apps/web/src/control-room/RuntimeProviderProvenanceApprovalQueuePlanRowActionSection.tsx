// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueuePlanRowActionSection({
  plan,
}: {
  plan: any;
}) {
  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            setSelectedProviderProvenanceSchedulerNarrativeGovernancePlanId(plan.plan_id);
          }}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id ? "Selected" : "Inspect"}
        </button>
      </div>
    </td>
  );
}
