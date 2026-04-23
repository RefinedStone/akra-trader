// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePlanDetailSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>
        {formatWorkflowToken(plan.action)} stitched_report_governance_registry
      </strong>
      <p className="run-lineage-symbol-copy">
        {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
      </p>
      <p className="run-lineage-symbol-copy">
        {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
      </p>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}
        {plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}
        {plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
      </p>
      {plan.policy_guidance ? (
        <p className="run-lineage-symbol-copy">{plan.policy_guidance}</p>
      ) : null}
    </td>
  );
}
