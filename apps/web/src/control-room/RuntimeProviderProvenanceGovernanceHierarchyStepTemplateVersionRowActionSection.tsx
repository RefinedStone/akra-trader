// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowActionSection({
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
            setEditingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId(
              entry.hierarchy_step_template_id,
            );
            setSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId(
              entry.hierarchy_step_template_id,
            );
            setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft({
              name: entry.name,
              description: entry.description,
              item_ids_text: entry.step.item_ids.join(", "),
              name_prefix: entry.step.name_prefix ?? "",
              name_suffix: entry.step.name_suffix ?? "",
              description_append: entry.step.description_append ?? "",
              query_patch: Object.keys(entry.step.query_patch ?? {}).length
                ? JSON.stringify(entry.step.query_patch, null, 2)
                : "",
              layout_patch: Object.keys(entry.step.layout_patch ?? {}).length
                ? JSON.stringify(entry.step.layout_patch, null, 2)
                : "",
              template_id: entry.step.template_id ?? "",
              clear_template_link: entry.step.clear_template_link,
              governance_policy_template_id: entry.governance_policy_template_id ?? "",
              governance_policy_catalog_id: entry.governance_policy_catalog_id ?? "",
              governance_approval_lane: entry.governance_approval_lane ?? "",
              governance_approval_priority: entry.governance_approval_priority ?? "",
            });
            setProviderProvenanceWorkspaceFeedback(
              `Hierarchy step template revision ${entry.revision_id} staged in the editor.`,
            );
          }}
          type="button"
        >
          Stage draft
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryRevision(
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
