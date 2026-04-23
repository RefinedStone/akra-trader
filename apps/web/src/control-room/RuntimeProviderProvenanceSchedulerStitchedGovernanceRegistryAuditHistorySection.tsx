// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditEventTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditEventTableSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterSelectSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterSelectSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterTextInputSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterTextInputSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionHistoryTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionHistoryTableSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditHistorySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched governance registry team audit</strong>
          <p>
            Review registry lifecycle and bulk governance changes by registry, actor, or
            reason without leaving the stitched-report governance surface.
          </p>
        </div>
        <div className="filter-bar">
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterSelectSection
            model={model}
          />
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterTextInputSection
            model={model}
          />
        </div>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading ? (
          <p className="empty-state">Loading stitched governance registry audit…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError ? (
          <p className="market-data-workflow-feedback">
            Stitched governance registry audit failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError}
          </p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.length ? (
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditEventTableSection
            model={model}
          />
        ) : (
          !providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading
            ? <p className="empty-state">No stitched governance registry audit events match the selected filters.</p>
            : null
        )}
      </div>
      {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryLoading ? (
        <p className="empty-state">Loading stitched governance registry history…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError ? (
        <p className="market-data-workflow-feedback">
          Registry history failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory ? (
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionHistoryTableSection
          model={model}
        />
      ) : null}
    </>
  );
}
