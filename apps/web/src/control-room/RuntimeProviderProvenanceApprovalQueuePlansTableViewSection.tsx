// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueuePlanRowDetailSection } from "./RuntimeProviderProvenanceApprovalQueuePlanRowDetailSection";
import { RuntimeProviderProvenanceApprovalQueuePlanRowActionSection } from "./RuntimeProviderProvenanceApprovalQueuePlanRowActionSection";

export function RuntimeProviderProvenanceApprovalQueuePlansTableViewSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>
            <input
              aria-label="Select all filtered governance plans"
              checked={
                filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length > 0
                && selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length === filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length
              }
              onChange={toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections}
              type="checkbox"
            />
          </th>
          <th>Plan</th>
          <th>Preview</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.map((plan) => (
          <tr
            key={plan.plan_id}
            className={
              selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
                ? "active-row"
                : undefined
            }
          >
            <td className="provider-provenance-selection-cell">
              <input
                aria-label={`Select governance plan ${plan.plan_id}`}
                checked={selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet.has(plan.plan_id)}
                onChange={() => {
                  toggleProviderProvenanceSchedulerNarrativeGovernancePlanSelection(plan.plan_id);
                }}
                type="checkbox"
              />
            </td>
            <RuntimeProviderProvenanceApprovalQueuePlanRowDetailSection plan={plan} />
            <RuntimeProviderProvenanceApprovalQueuePlanRowActionSection plan={plan} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
