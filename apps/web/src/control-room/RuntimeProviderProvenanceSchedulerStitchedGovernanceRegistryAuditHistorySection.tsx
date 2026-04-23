// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterSelectSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterSelectSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterTextInputSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterTextInputSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection";

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
          <table className="data-table">
            <thead>
              <tr>
                <th>When</th>
                <th>Action</th>
                <th>Actor</th>
                <th>Detail</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.map((entry) => (
                <tr key={`provider-scheduler-stitched-governance-registry-audit-${entry.audit_id}`}>
                  <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection
                    entry={entry}
                    model={model}
                  />
                  <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection
                    entry={entry}
                    model={model}
                  />
                  <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection
                    entry={entry}
                    model={model}
                  />
                  <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection
                    entry={entry}
                    model={model}
                  />
                </tr>
              ))}
            </tbody>
          </table>
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
        <table className="data-table">
          <thead>
            <tr>
              <th>Recorded</th>
              <th>Snapshot</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory.history.map((entry) => (
              <tr key={`provider-scheduler-stitched-governance-registry-revision-${entry.revision_id}`}>
                <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection
                  entry={entry}
                  model={model}
                />
                <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection
                  entry={entry}
                  model={model}
                />
                <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection
                  entry={entry}
                  model={model}
                />
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </>
  );
}
