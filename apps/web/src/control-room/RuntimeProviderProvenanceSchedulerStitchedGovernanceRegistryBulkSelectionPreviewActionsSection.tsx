// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionPreviewActionsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
