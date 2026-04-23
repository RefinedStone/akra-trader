// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSurfaceSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSurfaceSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSurfaceSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSurfaceSection";
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryReviewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSurfaceSection
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSurfaceSection
        model={model}
      />
    </>
  );
}
