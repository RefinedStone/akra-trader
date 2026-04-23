// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueAsyncStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueAsyncStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueEmptyStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueEmptyStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterPolicySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterPolicySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterQuerySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterQuerySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSummarySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSurfaceSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Stitched governance registry approval queue</strong>
        <p>
          Review staged governance plans for stitched-report governance registries
          without leaving the registry lifecycle workspace. This keeps queue-slice bundle
          approvals and rollback state next to the registry objects they mutate.
        </p>
      </div>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueSummarySection
        model={model}
      />
      <div className="filter-bar">
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterStateSection
          model={model}
        />
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterPolicySection
          model={model}
        />
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterQuerySection
          model={model}
        />
      </div>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueAsyncStateSection
        model={model}
      />
      {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.length ? (
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection
          model={model}
        />
      ) : (
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueEmptyStateSection
          model={model}
        />
      )}
    </div>
  );
}
