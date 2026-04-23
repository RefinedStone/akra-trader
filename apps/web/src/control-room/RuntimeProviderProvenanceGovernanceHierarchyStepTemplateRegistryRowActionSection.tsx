// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowActionSection({
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
            setSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId(
              entry.hierarchy_step_template_id,
            );
            setProviderProvenanceWorkspaceFeedback(
              `Selected hierarchy step template ${entry.name} for cross-catalog governance.`,
            );
          }}
          type="button"
        >
          Use template
        </button>
        <button
          className="ghost-button"
          disabled={entry.status !== "active"}
          onClick={() => {
            editProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(
              entry,
            );
          }}
          type="button"
        >
          Edit
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory(
              entry.hierarchy_step_template_id,
            );
          }}
          type="button"
        >
          Versions
        </button>
        <button
          className="ghost-button"
          disabled={entry.status !== "active"}
          onClick={() => {
            void stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateQueuePlan(
              entry,
            );
          }}
          type="button"
        >
          Stage queue
        </button>
        <button
          className="ghost-button"
          disabled={entry.status !== "active"}
          onClick={() => {
            void applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateToCatalogs(
              entry,
            );
          }}
          type="button"
        >
          Apply to selected catalogs
        </button>
        <button
          className="ghost-button"
          disabled={entry.status !== "active"}
          onClick={() => {
            void removeProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(
              entry,
            );
          }}
          type="button"
        >
          Delete
        </button>
      </div>
    </td>
  );
}
