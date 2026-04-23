// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerModerationApprovalQueueSection } from "./RuntimeProviderProvenanceSchedulerModerationApprovalQueueSection";
import { RuntimeProviderProvenanceSchedulerModerationPolicyCatalogSection } from "./RuntimeProviderProvenanceSchedulerModerationPolicyCatalogSection";

export function RuntimeProviderProvenanceSchedulerModerationGovernanceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerSearchDashboard ? (
        <>
          <RuntimeProviderProvenanceSchedulerModerationPolicyCatalogSection model={model} />
          <RuntimeProviderProvenanceSchedulerModerationApprovalQueueSection model={model} />
        </>
      ) : null}
      {providerProvenanceSchedulerSearchDashboardLoading ? (
        <p className="empty-state">Loading scheduler search dashboard…</p>
      ) : null}
      {providerProvenanceSchedulerSearchDashboardError ? (
        <p className="market-data-workflow-feedback">
          Scheduler search dashboard failed: {providerProvenanceSchedulerSearchDashboardError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading
      || providerProvenanceSchedulerSearchModerationPlansLoading
      || providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading
      || providerProvenanceSchedulerSearchModerationCatalogGovernancePlansLoading ? (
        <p className="empty-state">Loading scheduler moderation governance…</p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationPolicyCatalogsError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation policy catalogs failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation catalog governance policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation catalog governance queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationPlansError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation approval queue failed: {providerProvenanceSchedulerSearchModerationPlansError}
        </p>
      ) : null}
    </>
  );
}
