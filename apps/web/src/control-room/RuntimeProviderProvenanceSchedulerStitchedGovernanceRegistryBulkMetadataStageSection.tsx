// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataDescriptionStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataDescriptionStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataNameStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataNameStageSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataNameStageSection
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataDescriptionStageSection
        model={model}
      />
    </>
  );
}
