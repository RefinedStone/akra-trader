// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionButtonLayoutSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionButtonLayoutSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionCallbackWiringSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionCallbackWiringSection";

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
    <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionCallbackWiringSection
      handleOpenSharedCatalog={handleOpenSharedCatalog}
      handleStageQueue={handleStageQueue}
      handleUseDefaults={handleUseDefaults}
    >
      {({
        onOpenSharedCatalogClick,
        onStageQueueClick,
        onUseDefaultsClick,
      }: {
        onOpenSharedCatalogClick: () => void;
        onStageQueueClick: () => void;
        onUseDefaultsClick: () => void;
      }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionButtonLayoutSection
          onOpenSharedCatalogClick={onOpenSharedCatalogClick}
          onStageQueueClick={onStageQueueClick}
          onUseDefaultsClick={onUseDefaultsClick}
          stageQueueDisabled={stageQueueDisabled}
          useDefaultsDisabled={useDefaultsDisabled}
        />
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionCallbackWiringSection>
  );
}
