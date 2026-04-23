// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionToggleActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <button
      className="ghost-button"
      onClick={toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections}
      type="button"
    >
      {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
        === providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
        ? "Clear all"
        : "Select all"}
    </button>
  );
}
