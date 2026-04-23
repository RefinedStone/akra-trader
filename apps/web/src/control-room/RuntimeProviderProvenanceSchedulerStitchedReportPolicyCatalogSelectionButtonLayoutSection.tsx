// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionButtonLayoutSection({
  useDefaultsDisabled,
  stageQueueDisabled,
  onUseDefaultsClick,
  onStageQueueClick,
  onOpenSharedCatalogClick,
}: {
  useDefaultsDisabled: boolean;
  stageQueueDisabled: boolean;
  onUseDefaultsClick: () => void;
  onStageQueueClick: () => void;
  onOpenSharedCatalogClick: () => void;
}) {
  return (
    <>
      <button
        className="ghost-button"
        disabled={useDefaultsDisabled}
        onClick={onUseDefaultsClick}
        type="button"
      >
        Use defaults
      </button>
      <button
        className="ghost-button"
        disabled={stageQueueDisabled}
        onClick={onStageQueueClick}
        type="button"
      >
        Stage queue
      </button>
      <button
        className="ghost-button"
        onClick={onOpenSharedCatalogClick}
        type="button"
      >
        Open shared catalog
      </button>
    </>
  );
}
