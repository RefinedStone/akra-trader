// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionActionsSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionActionsSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionSummarySection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkEditSection({ model }: { model: any }) {
  return (
    <>
      {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
        <div className="provider-provenance-governance-bar">
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionSummarySection
            model={model}
          />
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkSelectionActionsSection
            model={model}
          />
        </div>
      ) : null}
      {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Bulk stitched governance registry edits</strong>
            <p>
              Preview queue-slice, default-policy, and metadata changes as staged
              governance plans before approval and apply.
            </p>
          </div>
          <div className="filter-bar">
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataStageSection
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueStageSection
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyStageSection
              model={model}
            />
          </div>
        </div>
      ) : null}
    </>
  );
}
