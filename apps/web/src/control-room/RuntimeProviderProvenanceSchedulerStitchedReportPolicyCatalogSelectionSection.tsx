// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={catalog.status !== "active"}
          onClick={() => {
            applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
          }}
          type="button"
        >
          Use defaults
        </button>
        <button
          className="ghost-button"
          disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
          onClick={() => {
            applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
            void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
          }}
          type="button"
        >
          Stage queue
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(
              catalog,
            );
          }}
          type="button"
        >
          Open shared catalog
        </button>
      </div>
    </td>
  );
}
