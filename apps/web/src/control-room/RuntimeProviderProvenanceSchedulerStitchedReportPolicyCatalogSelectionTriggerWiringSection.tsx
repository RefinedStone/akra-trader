// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionTriggerWiringSection({
  useDefaultsDisabled,
  stageQueueDisabled,
  handleUseDefaults,
  handleStageQueue,
  handleOpenSharedCatalog,
}: {
  useDefaultsDisabled: boolean;
  stageQueueDisabled: boolean;
  handleUseDefaults: () => void;
  handleStageQueue: () => void;
  handleOpenSharedCatalog: () => void;
}) {
  return (
    <>
      <button
        className="ghost-button"
        disabled={useDefaultsDisabled}
        onClick={handleUseDefaults}
        type="button"
      >
        Use defaults
      </button>
      <button
        className="ghost-button"
        disabled={stageQueueDisabled}
        onClick={handleStageQueue}
        type="button"
      >
        Stage queue
      </button>
      <button
        className="ghost-button"
        onClick={handleOpenSharedCatalog}
        type="button"
      >
        Open shared catalog
      </button>
    </>
  );
}
