// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionPerActionHandlersSection({
  applyCatalogDefaults,
  stageCatalogHierarchy,
  openSharedCatalog,
  children,
}: {
  applyCatalogDefaults: () => void;
  stageCatalogHierarchy: () => void;
  openSharedCatalog: () => void;
  children: any;
}) {
  const handleUseDefaults = () => {
    applyCatalogDefaults();
  };

  const handleStageQueue = () => {
    applyCatalogDefaults();
    stageCatalogHierarchy();
  };

  const handleOpenSharedCatalog = () => {
    openSharedCatalog();
  };

  return children({
    handleOpenSharedCatalog,
    handleStageQueue,
    handleUseDefaults,
  });
}
