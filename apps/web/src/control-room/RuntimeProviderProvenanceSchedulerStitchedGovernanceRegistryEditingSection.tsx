// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkEditSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkEditSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditingSection({ model }: { model: any }) {
  return (
    <div className="market-data-provenance-shared-history">
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkEditSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableSection model={model} />
    </div>
  );
}
