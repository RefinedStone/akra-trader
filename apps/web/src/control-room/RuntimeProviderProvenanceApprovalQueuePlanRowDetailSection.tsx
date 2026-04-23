// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueuePlanRowDetailSection({
  plan,
}: {
  plan: any;
}) {
  return (
    <>
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
    </>
  );
}
