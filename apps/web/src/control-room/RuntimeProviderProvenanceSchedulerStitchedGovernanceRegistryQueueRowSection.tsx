// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePlanDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePlanDetailSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePreviewDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePreviewDetailSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueRowSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePlanDetailSection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePreviewDetailSection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueActionSection
        model={model}
        plan={plan}
      />
    </>
  );
}
