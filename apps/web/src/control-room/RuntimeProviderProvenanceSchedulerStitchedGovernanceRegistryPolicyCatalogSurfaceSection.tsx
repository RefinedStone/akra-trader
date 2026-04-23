// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection";
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
      <div className="provider-provenance-governance-summary">
        <strong>
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length} registry catalog(s)
        </strong>
        <span>
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "active").length} active · {" "}
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "deleted").length} deleted
        </span>
      </div>
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
        <p className="empty-state">No stitched governance registry policy catalogs match the current search.</p>
      )}
    </div>
  );
}
