// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionActionsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-actions">
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
      <button
        className="ghost-button"
        disabled={
          !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
          || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction !== null
        }
        onClick={() => {
          void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
            "delete",
          );
        }}
        type="button"
      >
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "delete"
          ? "Previewing…"
          : "Preview delete"}
      </button>
      <button
        className="ghost-button"
        disabled={
          !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
          || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction !== null
        }
        onClick={() => {
          void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
            "restore",
          );
        }}
        type="button"
      >
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "restore"
          ? "Previewing…"
          : "Preview restore"}
      </button>
    </div>
  );
}
