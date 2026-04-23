// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkDeleteActionSection({
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
        void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("delete");
      }}
      type="button"
    >
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "delete"
        ? "Deleting…"
        : "Delete selected"}
    </button>
  );
}
