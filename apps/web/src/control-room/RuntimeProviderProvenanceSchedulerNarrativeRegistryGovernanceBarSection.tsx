// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryGovernanceBarSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-governance-bar">
      <div className="provider-provenance-governance-summary">
        <strong>
          {selectedProviderProvenanceSchedulerNarrativeRegistryIds.length} selected
        </strong>
        <span>
          {selectedProviderProvenanceSchedulerNarrativeRegistryEntries.filter((entry) => entry.status === "active").length} active ·{" "}
          {selectedProviderProvenanceSchedulerNarrativeRegistryEntries.filter((entry) => entry.status === "deleted").length} deleted
        </span>
      </div>
      <div className="market-data-provenance-history-actions">
        <label>
          <span>Policy</span>
          <select
            onChange={(event) => {
              setProviderProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId(event.target.value);
            }}
            value={providerProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId}
          >
            <option value="">No policy template</option>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
              .filter((entry) => entry.item_type_scope === "any" || entry.item_type_scope === "registry")
              .map((entry) => (
                <option key={entry.policy_template_id} value={entry.policy_template_id}>
                  {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                </option>
              ))}
          </select>
        </label>
        <button
          className="ghost-button"
          onClick={toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeRegistryIds.length === providerProvenanceSchedulerNarrativeRegistryEntries.length
            ? "Clear all"
            : "Select all"}
        </button>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeRegistryIds.length || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance("delete");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeRegistryBulkAction === "delete"
            ? "Previewing…"
            : "Preview delete"}
        </button>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeRegistryIds.length || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance("restore");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeRegistryBulkAction === "restore"
            ? "Previewing…"
            : "Preview restore"}
        </button>
      </div>
    </div>
  );
}
