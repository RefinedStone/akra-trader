// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueuePlansTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (providerProvenanceSchedulerNarrativeGovernancePlansLoading) {
    return <p className="empty-state">Loading governance plans…</p>;
  }

  if (providerProvenanceSchedulerNarrativeGovernancePlansError) {
    return (
      <p className="market-data-workflow-feedback">
        Governance plan registry load failed: {providerProvenanceSchedulerNarrativeGovernancePlansError}
      </p>
    );
  }

  if (!filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length) {
    return <p className="empty-state">No scheduler governance plans match the current approval queue filters.</p>;
  }

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
            <td>
              <strong>
                {formatWorkflowToken(plan.action)} {plan.item_type}
              </strong>
              <p className="run-lineage-symbol-copy">
                {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
              </p>
              <p className="run-lineage-symbol-copy">
                {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
              </p>
              <p className="run-lineage-symbol-copy">
                {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}{plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}{plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
              </p>
              {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(plan) ? (
                <p className="run-lineage-symbol-copy">
                  {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(plan)}
                </p>
              ) : null}
              {plan.policy_catalog_name ? (
                <p className="run-lineage-symbol-copy">
                  Source catalog {plan.policy_catalog_name}
                </p>
              ) : null}
              {plan.source_hierarchy_step_template_name || plan.source_hierarchy_step_template_id ? (
                <p className="run-lineage-symbol-copy">
                  Source hierarchy step template {plan.source_hierarchy_step_template_name ?? plan.source_hierarchy_step_template_id}
                </p>
              ) : null}
            </td>
            <td>
              <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
              <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
            </td>
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
          </tr>
        ))}
      </tbody>
    </table>
  );
}
