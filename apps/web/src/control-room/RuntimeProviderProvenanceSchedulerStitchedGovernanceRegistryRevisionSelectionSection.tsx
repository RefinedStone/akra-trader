// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSelectionSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <button
      className="ghost-button"
      onClick={() => {
        void toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory(
          entry.registry_id,
        );
      }}
      type="button"
    >
      {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryId === entry.registry_id
        && selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory
        ? "Hide versions"
        : "Versions"}
    </button>
  );
}
