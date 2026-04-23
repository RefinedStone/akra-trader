// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkRestoreActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <button
      className="ghost-button"
      disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
      onClick={() => {
        void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("restore");
      }}
      type="button"
    >
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "restore"
        ? "Restoring…"
        : "Restore selected"}
    </button>
  );
}
