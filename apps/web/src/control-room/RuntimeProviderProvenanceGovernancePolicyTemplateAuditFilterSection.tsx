// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateAuditFilterSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
