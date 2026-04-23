// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanApprovalSummarySection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(plan.approval_lane)} ·{" "}
        {formatWorkflowToken(plan.approval_priority)}
        {plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}
        {plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
      </p>
      {plan.policy_guidance ? (
        <p className="run-lineage-symbol-copy">{plan.policy_guidance}</p>
      ) : null}
    </>
  );
}
