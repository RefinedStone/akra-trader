// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection";
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
          <label>
            <span>Registry</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                  ...current,
                  registry_id: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.registry_id}
            >
              <option value="">All registries</option>
              {providerProvenanceSchedulerStitchedReportGovernanceRegistries.map((entry) => (
                <option key={entry.registry_id} value={entry.registry_id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Action</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                  ...current,
                  action: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.action}
            >
              <option value={ALL_FILTER_VALUE}>All actions</option>
              <option value="created">Created</option>
              <option value="updated">Updated</option>
              <option value="deleted">Deleted</option>
              <option value="restored">Restored</option>
            </select>
          </label>
          <label>
            <span>Actor tab</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                  ...current,
                  actor_tab_id: event.target.value,
                }))
              }
              placeholder="tab_ops"
              type="text"
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.actor_tab_id}
            />
          </label>
          <label>
            <span>Search</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
              placeholder="lag reviewed"
              type="text"
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.search}
            />
          </label>
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
