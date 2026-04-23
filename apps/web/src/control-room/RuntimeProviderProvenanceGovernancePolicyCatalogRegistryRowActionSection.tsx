// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowActionSection({
  catalog,
}: {
  catalog: any;
}) {
  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={catalog.status !== "active"}
          onClick={() => {
            applyProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
          }}
          type="button"
        >
          Apply catalog
        </button>
        <button
          className="ghost-button"
          disabled={catalog.status !== "active"}
          onClick={() => {
            void captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyForCatalog(catalog);
          }}
          type="button"
        >
          Capture hierarchy
        </button>
        <button
          className="ghost-button"
          disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
          onClick={() => {
            void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
          }}
          type="button"
        >
          Stage queue
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
          }}
          type="button"
        >
          Edit
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void removeProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
          }}
          type="button"
        >
          Delete
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory(
              catalog.catalog_id,
            );
          }}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId === catalog.catalog_id
            && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory
            ? "Hide versions"
            : "Versions"}
        </button>
      </div>
    </td>
  );
}
