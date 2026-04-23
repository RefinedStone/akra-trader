// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkUpdateActionSection({
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
        void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("update");
      }}
      type="button"
    >
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "update"
        ? "Updating…"
        : "Apply bulk edit"}
    </button>
  );
}
