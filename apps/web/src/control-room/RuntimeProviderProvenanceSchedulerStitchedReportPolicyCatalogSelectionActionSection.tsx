// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionSection({
  model,
  catalog,
  useDefaultsDisabled,
  stageQueueDisabled,
}: {
  model: any;
  catalog: any;
  useDefaultsDisabled: boolean;
  stageQueueDisabled: boolean;
}) {
  const {
    applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog,
    stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy,
    openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface,
  } = model;

  return (
    <>
      <button
        className="ghost-button"
        disabled={useDefaultsDisabled}
        onClick={() => {
          applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
        }}
        type="button"
      >
        Use defaults
      </button>
      <button
        className="ghost-button"
        disabled={stageQueueDisabled}
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
