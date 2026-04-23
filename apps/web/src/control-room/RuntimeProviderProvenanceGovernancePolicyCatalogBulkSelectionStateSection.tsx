// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionStateSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
