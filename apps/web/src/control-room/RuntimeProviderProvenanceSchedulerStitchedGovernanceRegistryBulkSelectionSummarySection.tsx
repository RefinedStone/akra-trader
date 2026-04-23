// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionSummarySection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="provider-provenance-governance-summary">
      <strong>
        {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length} selected
      </strong>
      <span>
        {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "active").length} active ·{" "}
        {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "deleted").length} deleted
      </span>
    </div>
  );
}
