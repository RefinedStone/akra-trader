// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionCallbackWiringSection({
  handleUseDefaults,
  handleStageQueue,
  handleOpenSharedCatalog,
  children,
}: {
  handleUseDefaults: () => void;
  handleStageQueue: () => void;
  handleOpenSharedCatalog: () => void;
  children: any;
}) {
  const onUseDefaultsClick = () => {
    handleUseDefaults();
  };

  const onStageQueueClick = () => {
    handleStageQueue();
  };

  const onOpenSharedCatalogClick = () => {
    handleOpenSharedCatalog();
  };

  return children({
    onOpenSharedCatalogClick,
    onStageQueueClick,
    onUseDefaultsClick,
  });
}
