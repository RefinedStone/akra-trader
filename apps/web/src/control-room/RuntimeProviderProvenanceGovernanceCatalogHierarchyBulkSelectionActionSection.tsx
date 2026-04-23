// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Action</span>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction("delete");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction === "delete"
            ? "Deleting…"
            : "Delete selected"}
        </button>
      </label>
      <label>
        <span>Action</span>
        <button
          className="ghost-button"
          disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction("update");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction === "update"
            ? "Updating…"
            : "Update selected"}
        </button>
      </label>
    </>
  );
}
