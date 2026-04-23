// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkEditStageSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkEditStageSection";
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryGovernanceBarSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryGovernanceBarSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkGovernanceSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return providerProvenanceSchedulerNarrativeRegistryEntries.length ? (
    <>
      <RuntimeProviderProvenanceSchedulerNarrativeRegistryGovernanceBarSection model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkEditStageSection model={model} />
    </>
  ) : null;
}
