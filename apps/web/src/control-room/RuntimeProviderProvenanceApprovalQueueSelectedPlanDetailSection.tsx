// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueSelectedPlanDetailSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeGovernancePlan ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Selected plan</strong>
        <p>
          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.action)} {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.item_type} ·{" "}
          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status)} ·{" "}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.length} preview row(s)
        </p>
      </div>
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
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={
            selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "previewed"
            || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
          }
          onClick={() => {
            void approveProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
            ? "Approving…"
            : "Approve plan"}
        </button>
        <button
          className="ghost-button"
          disabled={
            selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "approved"
            || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
          }
          onClick={() => {
            void applyProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
            ? "Applying…"
            : "Apply approved plan"}
        </button>
        <button
          className="ghost-button"
          disabled={
            selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "applied"
            || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
          }
          onClick={() => {
            void rollbackProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
            ? "Rolling back…"
            : "Rollback plan"}
        </button>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Diff preview</th>
            <th>Rollback</th>
          </tr>
        </thead>
        <tbody>
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.map((item) => (
            <tr key={item.item_id}>
              <td>
                <strong>{item.item_name ?? item.item_id}</strong>
                <p className="run-lineage-symbol-copy">
                  {formatWorkflowToken(item.outcome)} · {formatWorkflowToken(item.status ?? "unknown")}
                </p>
                <p className="run-lineage-symbol-copy">
                  {item.message ?? "No preview note."}
                </p>
              </td>
              <td>
                <strong>
                  {item.changed_fields.length ? item.changed_fields.join(", ") : "No field changes"}
                </strong>
                {item.changed_fields.length ? (
                  <div className="provider-provenance-governance-summary">
                    {item.changed_fields.map((fieldName) => (
                      <span key={fieldName}>
                        {fieldName}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.before)} {"->"}{" "}
                        {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.after)}
                      </span>
                    ))}
                  </div>
                ) : null}
              </td>
              <td>
                <strong>
                  {item.rollback_revision_id
                    ? shortenIdentifier(item.rollback_revision_id, 10)
                    : "No rollback revision"}
                </strong>
                <p className="run-lineage-symbol-copy">
                  current {item.current_revision_id ? shortenIdentifier(item.current_revision_id, 10) : "n/a"}
                </p>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result ? (
        <p className="run-lineage-symbol-copy">
          Apply result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result)}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result ? (
        <p className="run-lineage-symbol-copy">
          Rollback result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result)}
        </p>
      ) : null}
    </div>
  ) : null;
}
