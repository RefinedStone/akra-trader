// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogWorkflowSection({ model }: { model: any }) {
  const {} = model;

  return providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length ? (
    <div className="provider-provenance-governance-editor">
      <div className="market-data-provenance-history-head">
        <strong>Policy catalog workflow</strong>
        <p>Bundle selected governance policy templates into a reusable catalog and reapply its queue/default-policy context later.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Selection</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelections}
              type="button"
            >
              {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds.length === providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length
                ? "Clear all"
                : "Select all"}
            </button>
          </div>
          <p className="run-lineage-symbol-copy">
            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries.length} template(s) selected
          </p>
        </label>
        <label>
          <span>Catalog name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Shift lead governance catalog"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="High-signal batch policies"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft.description}
          />
        </label>
        <label>
          <span>Default template</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft((current) => ({
                ...current,
                default_policy_template_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft.default_policy_template_id}
          >
            <option value="">First selected template</option>
            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries.map((entry) => (
              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries.length}
              onClick={() => {
                void saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId
                ? "Update catalog"
                : "Save catalog"}
            </button>
            {editingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId ? (
              <button
                className="ghost-button"
                onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft}
                type="button"
              >
                Cancel edit
              </button>
            ) : (
              <button
                className="ghost-button"
                onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft}
                type="button"
              >
                Reset
              </button>
            )}
          </div>
        </label>
      </div>
    </div>
  ) : null;
}
