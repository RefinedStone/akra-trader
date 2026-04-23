// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicyApprovalEscalationActionSection({
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
    </>
  );
}
