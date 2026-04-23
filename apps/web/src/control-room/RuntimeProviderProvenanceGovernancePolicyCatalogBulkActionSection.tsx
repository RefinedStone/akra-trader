// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Action</span>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("delete");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "delete"
            ? "Deleting…"
            : "Delete selected"}
        </button>
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
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("update");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "update"
            ? "Updating…"
            : "Apply bulk edit"}
        </button>
      </div>
    </label>
  );
}
