// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueSelectedPlanSummarySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <div className="provider-provenance-governance-summary">
        <strong>{selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_summary}</strong>
        <span>
          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approval_lane)} · {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approval_priority)}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_template_name
            ? ` · ${selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_template_name}`
            : ""}{" "}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_catalog_name
            ? ` · ${selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_catalog_name}`
            : ""}{" "}
          ·{" "}
          Approval {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approved_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approved_at) : "pending"} ·{" "}
          Apply {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_at) : "not applied"} ·{" "}
          Rollback {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rolled_back_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rolled_back_at) : "not rolled back"}
        </span>
      </div>
      {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(selectedProviderProvenanceSchedulerNarrativeGovernancePlan) ? (
        <p className="run-lineage-symbol-copy">
          Hierarchy: {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(selectedProviderProvenanceSchedulerNarrativeGovernancePlan)}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_guidance ? (
        <p className="run-lineage-symbol-copy">
          Guidance: {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_guidance}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_name
      || selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_id ? (
        <p className="run-lineage-symbol-copy">
          Source hierarchy step template: {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_name
            ?? selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_id}
        </p>
      ) : null}
    </>
  );
}
