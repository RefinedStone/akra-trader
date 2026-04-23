// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogAuditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
          <div className="market-data-provenance-shared-history">
            <div className="market-data-provenance-history-head">
              <strong>Policy catalog team audit</strong>
              <p>Filter shared audit events by catalog, action, or actor to review catalog lifecycle and linked-template changes.</p>
            </div>
            <div className="filter-bar">
              <label>
                <span>Catalog</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                      ...current,
                      catalog_id: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.catalog_id}
                >
                  <option value="">All catalogs</option>
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((entry) => (
                    <option key={entry.catalog_id} value={entry.catalog_id}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Action</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                      ...current,
                      action: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.action}
                >
                  <option value={ALL_FILTER_VALUE}>All actions</option>
                  <option value="created">Created</option>
                  <option value="updated">Updated</option>
                  <option value="hierarchy_captured">Hierarchy captured</option>
                  <option value="hierarchy_step_updated">Hierarchy step updated</option>
                  <option value="hierarchy_step_restored">Hierarchy step restored</option>
                  <option value="hierarchy_steps_bulk_updated">Hierarchy steps bulk updated</option>
                  <option value="hierarchy_steps_bulk_deleted">Hierarchy steps bulk deleted</option>
                  <option value="staged">Staged</option>
                  <option value="deleted">Deleted</option>
                  <option value="restored">Restored</option>
                </select>
              </label>
              <label>
                <span>Actor</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                      ...current,
                      actor_tab_id: event.target.value,
                    }))
                  }
                  placeholder="tab_ops"
                  type="text"
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.actor_tab_id}
                />
              </label>
              <label>
                <span>Search</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                      ...current,
                      search: event.target.value,
                    }))
                  }
                  placeholder="batch, restore, default"
                  type="search"
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.search}
                />
              </label>
              <label>
                <span>Action</span>
                <button
                  className="ghost-button"
                  onClick={() => {
                    void loadProviderProvenanceWorkspaceRegistry();
                  }}
                  type="button"
                >
                  Refresh audit
                </button>
              </label>
            </div>
            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsLoading ? (
              <p className="empty-state">Loading policy catalog audit trail…</p>
            ) : null}
            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsError ? (
              <p className="market-data-workflow-feedback">
                Policy catalog audit load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsError}
              </p>
            ) : null}
            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Audit</th>
                    <th>Catalog</th>
                    <th>Actor</th>
                  </tr>
                </thead>
                <tbody>
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits.map((entry) => (
                    <tr key={entry.audit_id}>
                      <td>
                        <strong>{formatWorkflowToken(entry.action)}</strong>
                        <p className="run-lineage-symbol-copy">
                          {entry.detail}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          {formatTimestamp(entry.recorded_at)}
                        </p>
                      </td>
                      <td>
                        <strong>{entry.name}</strong>
                        <p className="run-lineage-symbol-copy">
                          {formatWorkflowToken(entry.status)} · {entry.policy_template_names.join(", ") || "No linked templates."}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(entry.hierarchy_steps)}
                        </p>
                      </td>
                      <td>
                        <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "system"}</strong>
                        <p className="run-lineage-symbol-copy">
                          {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          {entry.reason}
                        </p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">No policy catalog audit records match the current filter.</p>
            )}
          </div>
    </>
  );
}
