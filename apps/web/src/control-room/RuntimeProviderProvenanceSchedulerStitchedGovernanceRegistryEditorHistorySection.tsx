// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditHistorySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditHistorySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditingSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditingSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditorHistorySection({ model }: { model: any }) {
  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditingSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditHistorySection model={model} />
    </>
  );
}
