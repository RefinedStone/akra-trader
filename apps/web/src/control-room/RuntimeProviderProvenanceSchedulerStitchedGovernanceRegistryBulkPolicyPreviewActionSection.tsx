// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyPreviewActionSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-actions">
      <button
        className="ghost-button"
        disabled={
          !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
          || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction
          !== null
        }
        onClick={() => {
          void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
            "update",
          );
        }}
        type="button"
      >
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "update"
          ? "Previewing…"
          : "Preview bulk edit"}
      </button>
    </div>
  );
}
