// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSharedDispatchPlumbingSection({
  model,
  catalog,
  children,
}: {
  model: any;
  catalog: any;
  children: any;
}) {
  const {
    applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog,
    stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy,
    openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface,
  } = model;

  const applyCatalogDefaults = () => {
    applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
  };

  const stageCatalogHierarchy = () => {
    void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
  };

  const openSharedCatalog = () => {
    openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(
      catalog,
    );
  };

  return children({
    applyCatalogDefaults,
    openSharedCatalog,
    stageCatalogHierarchy,
  });
}
