// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionDispatchSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionDispatchSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionTriggerWiringSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionTriggerWiringSection";

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
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionDispatchSection
      catalog={catalog}
      model={model}
    >
      {({
        handleOpenSharedCatalog,
        handleStageQueue,
        handleUseDefaults,
      }: {
        handleOpenSharedCatalog: () => void;
        handleStageQueue: () => void;
        handleUseDefaults: () => void;
      }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionTriggerWiringSection
          handleOpenSharedCatalog={handleOpenSharedCatalog}
          handleStageQueue={handleStageQueue}
          handleUseDefaults={handleUseDefaults}
          stageQueueDisabled={stageQueueDisabled}
          useDefaultsDisabled={useDefaultsDisabled}
        />
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionDispatchSection>
  );
}
