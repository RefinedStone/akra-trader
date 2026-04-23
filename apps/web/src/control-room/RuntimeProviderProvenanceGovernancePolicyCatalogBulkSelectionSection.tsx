// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Selection</span>
      <button
        className="ghost-button"
        onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelections}
        type="button"
      >
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds.length
          === providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length
          ? "Clear all"
          : "Select all"}
      </button>
      <p className="run-lineage-symbol-copy">
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length} catalog(s) selected
      </p>
    </label>
  );
}
