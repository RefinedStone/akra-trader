// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateAuditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Policy template team audit</strong>
        <p>Filter shared audit events by template, action, or actor to review who changed governance defaults.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Template</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                ...current,
                policy_template_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.policy_template_id}
          >
            <option value="">All templates</option>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Action</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                ...current,
                action: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.action}
          >
            <option value={ALL_FILTER_VALUE}>All actions</option>
            <option value="created">Created</option>
            <option value="updated">Updated</option>
            <option value="deleted">Deleted</option>
            <option value="restored">Restored</option>
          </select>
        </label>
        <label>
          <span>Actor</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                ...current,
                actor_tab_id: event.target.value,
              }))
            }
            placeholder="tab_ops"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.actor_tab_id}
          />
        </label>
        <label>
          <span>Search</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                ...current,
                search: event.target.value,
              }))
            }
            placeholder="shift lead, restore"
            type="search"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.search}
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
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsLoading ? (
        <p className="empty-state">Loading policy template audit trail…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError ? (
        <p className="market-data-workflow-feedback">
          Policy template audit load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Audit</th>
              <th>Template</th>
              <th>Actor</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits.map((entry) => (
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
                    {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.item_type_scope)} / {formatWorkflowToken(entry.action_scope)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
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
        <p className="empty-state">No policy template audit records match the current filter.</p>
      )}
    </div>
  );
}
