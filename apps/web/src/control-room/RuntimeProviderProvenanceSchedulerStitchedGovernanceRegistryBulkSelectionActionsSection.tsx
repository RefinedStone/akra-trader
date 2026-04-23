// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionPreviewActionsSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionPreviewActionsSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionToggleActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionToggleActionSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionActionsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-actions">
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionToggleActionSection
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionPreviewActionsSection
        model={model}
      />
    </div>
  );
}
