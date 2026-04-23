// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowActionSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId(
              entry.policy_template_id,
            );
            setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft({
              name: entry.name,
              description: entry.description,
              item_type_scope:
                entry.item_type_scope === "template"
                || entry.item_type_scope === "registry"
                || entry.item_type_scope === "stitched_report_view"
                || entry.item_type_scope === "stitched_report_governance_registry"
                  ? entry.item_type_scope
                  : "any",
              action_scope:
                entry.action_scope === "delete"
                || entry.action_scope === "restore"
                || entry.action_scope === "update"
                  ? entry.action_scope
                  : "any",
              approval_lane: entry.approval_lane,
              approval_priority:
                entry.approval_priority === "low"
                || entry.approval_priority === "high"
                || entry.approval_priority === "critical"
                  ? entry.approval_priority
                  : "normal",
              guidance: entry.guidance ?? "",
            });
            setProviderProvenanceWorkspaceFeedback(
              `Policy template revision ${entry.revision_id} staged in the editor.`,
            );
          }}
          type="button"
        >
          Stage draft
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryRevision(
              entry,
            );
          }}
          type="button"
        >
          Restore revision
        </button>
      </div>
    </td>
  );
}
