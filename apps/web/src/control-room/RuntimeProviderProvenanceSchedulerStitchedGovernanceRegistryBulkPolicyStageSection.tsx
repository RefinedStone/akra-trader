// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkDefaultPolicyStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkDefaultPolicyStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkGovernancePolicyStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkGovernancePolicyStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyPreviewActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyPreviewActionSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkDefaultPolicyStageSection
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkGovernancePolicyStageSection
        model={model}
      />
      <label>
        <span>Action</span>
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyPreviewActionSection
          model={model}
        />
      </label>
    </>
  );
}
