// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Hierarchy step template team audit</strong>
          <p>Filter lifecycle and bulk-governance events by template, action, or actor to review who changed reusable cross-catalog steps.</p>
        </div>
        <div className="filter-bar">
          <label>
            <span>Template</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                  ...current,
                  hierarchy_step_template_id: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.hierarchy_step_template_id}
            >
              <option value="">All templates</option>
              {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
                <option key={entry.hierarchy_step_template_id} value={entry.hierarchy_step_template_id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Action</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                  ...current,
                  action: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.action}
            >
              <option value={ALL_FILTER_VALUE}>All actions</option>
              <option value="created">Created</option>
              <option value="updated">Updated</option>
              <option value="staged">Staged</option>
              <option value="deleted">Deleted</option>
              <option value="restored">Restored</option>
            </select>
          </label>
          <label>
            <span>Actor</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                  ...current,
                  actor_tab_id: event.target.value,
                }))
              }
              placeholder="tab_ops"
              type="text"
              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.actor_tab_id}
            />
          </label>
          <label>
            <span>Search</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
              placeholder="cross-catalog, bulk"
              type="search"
              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.search}
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
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsLoading ? (
          <p className="empty-state">Loading hierarchy step template audit trail…</p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError ? (
          <p className="market-data-workflow-feedback">
            Hierarchy step template audit load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError}
          </p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Audit</th>
                <th>Template</th>
                <th>Actor</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits.map((entry) => (
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
                      {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                    </p>
                    {(entry.governance_policy_template_name || entry.governance_policy_catalog_name || entry.governance_approval_lane || entry.governance_approval_priority) ? (
                      <p className="run-lineage-symbol-copy">
                        Queue policy: {entry.governance_policy_template_name ?? "no template"}
                        {entry.governance_policy_catalog_name ? ` · ${entry.governance_policy_catalog_name}` : ""}
                        {entry.governance_approval_lane ? ` · ${formatWorkflowToken(entry.governance_approval_lane)}` : ""}
                        {entry.governance_approval_priority ? ` · ${formatWorkflowToken(entry.governance_approval_priority)}` : ""}
                      </p>
                    ) : null}
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.item_type)}
                      {entry.origin_catalog_name ? ` · ${entry.origin_catalog_name}` : " · ad hoc source"}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
                    </p>
                  </td>
                  <td>
                    <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "system"}</strong>
                    <p className="run-lineage-symbol-copy">
                      {entry.reason}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {entry.origin_step_id ? `Origin step ${entry.origin_step_id}` : "No origin step"}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty-state">No hierarchy step template audit records match the current filter.</p>
        )}
      </div>
    </>
  );
}
