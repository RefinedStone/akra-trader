// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionStateSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
