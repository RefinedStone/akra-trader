// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueRowSection({
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
      <td>
        <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
        <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
        <p className="run-lineage-symbol-copy">
          {plan.preview_items.length} preview row(s) · rollback ready {plan.rollback_ready_count}
        </p>
      </td>
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
    </>
  );
}
