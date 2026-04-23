// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterPolicySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterPolicySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterQuerySection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterQuerySection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection";
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryReviewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched governance registry approval queue</strong>
          <p>
            Review staged governance plans for stitched-report governance registries
            without leaving the registry lifecycle workspace. This keeps queue-slice bundle
            approvals and rollback state next to the registry objects they mutate.
          </p>
        </div>
        <div className="provider-provenance-governance-summary">
          <strong>
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.total} registry plan(s)
          </strong>
          <span>
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.pending_approval_count} pending approval · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.ready_to_apply_count} ready to apply · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.completed_count} completed
          </span>
        </div>
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
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading ? (
          <p className="empty-state">Loading stitched governance registry approval queue…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError ? (
          <p className="market-data-workflow-feedback">
            Stitched governance registry approval queue failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError}
          </p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.length ? (
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection
            model={model}
          />
        ) : (
          !providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading
            ? <p className="empty-state">No stitched governance registry plans match the dedicated queue filters.</p>
            : null
        )}
      </div>
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
    </>
  );
}
