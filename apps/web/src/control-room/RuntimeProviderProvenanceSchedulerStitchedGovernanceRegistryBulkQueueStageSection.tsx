// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueCoreStateStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueCoreStateStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueQueryStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueQueryStageSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueCoreStateStageSection
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueQueryStageSection
        model={model}
      />
    </>
  );
}
