// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicyActionSection({
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
          void updateSharedProviderProvenanceSchedulerExportPolicy(
            selectedProviderProvenanceSchedulerExportEntry,
          );
        }}
        type="button"
      >
        Save policy
      </button>
      <button
        className="ghost-button"
        disabled={
          !selectedProviderProvenanceSchedulerExportEntry.approval_required ||
          selectedProviderProvenanceSchedulerExportEntry.approval_state === "approved"
        }
        onClick={() => {
          void approveSharedProviderProvenanceSchedulerExport(
            selectedProviderProvenanceSchedulerExportEntry,
          );
        }}
        type="button"
      >
        Approve route
      </button>
      <button
        className="ghost-button"
        disabled={
          selectedProviderProvenanceSchedulerExportEntry.approval_required &&
          selectedProviderProvenanceSchedulerExportEntry.approval_state !== "approved"
        }
        onClick={() => {
          void escalateSharedProviderProvenanceSchedulerExport(
            selectedProviderProvenanceSchedulerExportEntry,
          );
        }}
        type="button"
      >
        Escalate now
      </button>
    </div>
  );
}
