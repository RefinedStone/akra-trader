// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <>
      <td>
        <strong>{formatWorkflowToken(plan.action)} stitched_report_view</strong>
        <p className="run-lineage-symbol-copy">
          {shortenIdentifier(plan.plan_id, 10)} ·{" "}
          {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
        </p>
        <p className="run-lineage-symbol-copy">
          {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} ·{" "}
          {formatTimestamp(plan.updated_at)}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(plan.approval_lane)} ·{" "}
          {formatWorkflowToken(plan.approval_priority)}
          {plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}
          {plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
        </p>
        {plan.policy_guidance ? (
          <p className="run-lineage-symbol-copy">{plan.policy_guidance}</p>
        ) : null}
      </td>
      <td>
        <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
        <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
        <p className="run-lineage-symbol-copy">
          {plan.preview_items.length} preview row(s) · rollback ready{" "}
          {plan.rollback_ready_count}
        </p>
      </td>
    </>
  );
}
