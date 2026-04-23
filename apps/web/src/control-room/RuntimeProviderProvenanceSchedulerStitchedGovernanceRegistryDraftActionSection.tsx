// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-actions">
      <button
        className="ghost-button"
        onClick={() => {
          void saveCurrentProviderProvenanceSchedulerStitchedReportGovernanceRegistry();
        }}
        type="button"
      >
        {editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId
          ? "Update registry"
          : "Save registry"}
      </button>
      {editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId ? (
        <button
          className="ghost-button"
          onClick={() => {
            resetProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft();
          }}
          type="button"
        >
          Cancel edit
        </button>
      ) : null}
    </div>
  );
}
