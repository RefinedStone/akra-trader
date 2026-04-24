// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplateGovernanceBarSection({
  model,
}: {
  model: any;
}) {
  const {
    formatWorkflowToken,
    providerProvenanceSchedulerNarrativeGovernancePolicyTemplates,
    providerProvenanceSchedulerNarrativeTemplateBulkAction,
    providerProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId,
    providerProvenanceSchedulerNarrativeTemplates,
    runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance,
    selectedProviderProvenanceSchedulerNarrativeTemplateEntries,
    selectedProviderProvenanceSchedulerNarrativeTemplateIds,
    setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId,
    toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections,
  } = model;

  return (
    <div className="provider-provenance-governance-bar">
      <div className="provider-provenance-governance-summary">
        <strong>
          {selectedProviderProvenanceSchedulerNarrativeTemplateIds.length} selected
        </strong>
        <span>
          {selectedProviderProvenanceSchedulerNarrativeTemplateEntries.filter((entry) => entry.status === "active").length} active ·{" "}
          {selectedProviderProvenanceSchedulerNarrativeTemplateEntries.filter((entry) => entry.status === "deleted").length} deleted
        </span>
      </div>
      <div className="market-data-provenance-history-actions">
        <label>
          <span>Policy</span>
          <select
            onChange={(event) => {
              setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId(event.target.value);
            }}
            value={providerProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId}
          >
            <option value="">No policy template</option>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
              .filter((entry) => entry.item_type_scope === "any" || entry.item_type_scope === "template")
              .map((entry) => (
                <option key={entry.policy_template_id} value={entry.policy_template_id}>
                  {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                </option>
              ))}
          </select>
        </label>
        <button
          className="ghost-button"
          onClick={toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeTemplateIds.length === providerProvenanceSchedulerNarrativeTemplates.length
            ? "Clear all"
            : "Select all"}
        </button>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeTemplateIds.length || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance("delete");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeTemplateBulkAction === "delete"
            ? "Previewing…"
            : "Preview delete"}
        </button>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeTemplateIds.length || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance("restore");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeTemplateBulkAction === "restore"
            ? "Previewing…"
            : "Preview restore"}
        </button>
      </div>
    </div>
  );
}
