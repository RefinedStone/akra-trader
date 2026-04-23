// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkSelectionStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <div className="filter-bar">
        <label>
          <span>Selection</span>
          <button
            className="ghost-button"
            disabled={!providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length}
            onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelections}
            type="button"
          >
            {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length
              === providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length
              && providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length
                ? "Clear all"
                : "Select all"}
          </button>
        </label>
        <label>
          <span>Bulk name prefix</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                ...current,
                name_prefix: event.target.value,
              }))
            }
            placeholder="Reviewed / "
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.name_prefix}
          />
        </label>
        <label>
          <span>Bulk name suffix</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                ...current,
                name_suffix: event.target.value,
              }))
            }
            placeholder=" / staged"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.name_suffix}
          />
        </label>
        <label>
          <span>Bulk description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                ...current,
                description_append: event.target.value,
              }))
            }
            placeholder="team rollout"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.description_append}
          />
        </label>
        <label>
          <span>Bulk targets</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                ...current,
                item_ids_text: event.target.value,
              }))
            }
            placeholder="optional override ids"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.item_ids_text}
          />
        </label>
        <label>
          <span>Action</span>
          <button
            className="ghost-button"
            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
            onClick={() => {
              void runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction("delete");
            }}
            type="button"
          >
            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "delete"
              ? "Deleting…"
              : "Delete selected"}
          </button>
        </label>
        <label>
          <span>Action</span>
          <button
            className="ghost-button"
            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
            onClick={() => {
              void runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction("restore");
            }}
            type="button"
          >
            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "restore"
              ? "Restoring…"
              : "Restore selected"}
          </button>
        </label>
        <label>
          <span>Action</span>
          <button
            className="ghost-button"
            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
            onClick={() => {
              void stageSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates();
            }}
            type="button"
          >
            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "stage"
              ? "Staging…"
              : "Stage selected"}
          </button>
        </label>
        <label>
          <span>Action</span>
          <button
            className="ghost-button"
            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
            onClick={() => {
              void runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction("update");
            }}
            type="button"
          >
            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "update"
              ? "Updating…"
              : "Update selected"}
          </button>
        </label>
      </div>
    </>
  );
}
