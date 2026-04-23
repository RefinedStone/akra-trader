// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStateSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Selection</span>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length}
          onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelections}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length
            === selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length
            && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length
            ? "Clear all"
            : "Select all"}
        </button>
      </label>
      <label>
        <span>Bulk name prefix</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              name_prefix: event.target.value,
            }))
          }
          placeholder="Reviewed / "
          type="text"
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.name_prefix}
        />
      </label>
      <label>
        <span>Bulk name suffix</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              name_suffix: event.target.value,
            }))
          }
          placeholder=" / approved"
          type="text"
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.name_suffix}
        />
      </label>
      <label>
        <span>Bulk description</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              description_append: event.target.value,
            }))
          }
          placeholder="shared governance note"
          type="text"
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.description_append}
        />
      </label>
      <label>
        <span>Bulk template link</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              template_id: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.template_id}
        >
          <option value="">Keep current link</option>
          {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
            <option key={entry.template_id} value={entry.template_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Clear link</span>
        <input
          checked={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.clear_template_link}
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              clear_template_link: event.target.checked,
            }))
          }
          type="checkbox"
        />
      </label>
    </>
  );
}
