// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogEmptyStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogEmptyStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSummarySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSurfaceSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Stitched governance registry policy catalogs</strong>
        <p>
          Review only governance catalogs that can drive stitched-governance-registry
          approvals, then apply those defaults or jump into the shared catalog workspace
          when deeper hierarchy maintenance is needed.
        </p>
      </div>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSummarySection
        model={model}
      />
      <div className="filter-bar">
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection
          model={model}
        />
      </div>
      {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length ? (
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection
          model={model}
        />
      ) : (
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogEmptyStateSection
          model={model}
        />
      )}
    </div>
  );
}
