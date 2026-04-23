// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionDispatchSection({
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

  const handleUseDefaults = () => {
    applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
  };

  const handleStageQueue = () => {
    applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
    void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
  };

  const handleOpenSharedCatalog = () => {
    openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(
      catalog,
    );
  };

  return children({
    handleOpenSharedCatalog,
    handleStageQueue,
    handleUseDefaults,
  });
}
