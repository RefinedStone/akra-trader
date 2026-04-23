// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportAuditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Stitched report view team audit</strong>
        <p>
          Filter shared audit rows by saved view, action, or actor to review bulk governance
          and lifecycle changes.
        </p>
      </div>
      <div className="filter-bar">
        <label>
          <span>View</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                ...current,
                view_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerStitchedReportViewAuditFilter.view_id}
          >
            <option value="">All views</option>
            {providerProvenanceSchedulerStitchedReportViews.map((entry) => (
              <option key={entry.view_id} value={entry.view_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Action</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                ...current,
                action: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerStitchedReportViewAuditFilter.action}
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
              setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                ...current,
                actor_tab_id: event.target.value,
              }))
            }
            placeholder="tab_ops"
            type="text"
            value={providerProvenanceSchedulerStitchedReportViewAuditFilter.actor_tab_id}
          />
        </label>
        <label>
          <span>Search</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                ...current,
                search: event.target.value,
              }))
            }
            placeholder="lag recovery"
            type="text"
            value={providerProvenanceSchedulerStitchedReportViewAuditFilter.search}
          />
        </label>
      </div>
      {providerProvenanceSchedulerStitchedReportViewAuditsLoading ? (
        <p className="empty-state">Loading stitched report view audit…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViewAuditsError ? (
        <p className="market-data-workflow-feedback">
          Stitched report view audit failed:{" "}
          {providerProvenanceSchedulerStitchedReportViewAuditsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViewAudits.length ? (
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
            {providerProvenanceSchedulerStitchedReportViewAudits.map((entry) => (
              <tr key={`provider-scheduler-stitched-view-audit-${entry.audit_id}`}>
                <td>
                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                  <p className="run-lineage-symbol-copy">{entry.name}</p>
                </td>
                <td>
                  <strong>{formatWorkflowToken(entry.action)}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.status)} · {entry.filter_summary}
                  </p>
                </td>
                <td>
                  <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.actor_tab_id ?? "No tab id recorded."}
                  </p>
                </td>
                <td>
                  <strong>{entry.detail}</strong>
                  <p className="run-lineage-symbol-copy">{entry.reason}</p>
                  <p className="run-lineage-symbol-copy">
                    {entry.occurrence_limit} occurrence(s) · history {entry.history_limit} ·
                    drill-down {entry.drilldown_history_limit}
                  </p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : !providerProvenanceSchedulerStitchedReportViewAuditsLoading ? (
        <p className="empty-state">
          No stitched report view audit events match the selected filters.
        </p>
      ) : null}
    </div>
  );
}
