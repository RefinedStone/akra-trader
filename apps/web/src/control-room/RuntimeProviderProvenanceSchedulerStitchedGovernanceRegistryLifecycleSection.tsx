// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditorHistorySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditorHistorySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryReviewSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryReviewSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryLifecycleSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryReviewSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditorHistorySection model={model} />
    </>
  );
}
