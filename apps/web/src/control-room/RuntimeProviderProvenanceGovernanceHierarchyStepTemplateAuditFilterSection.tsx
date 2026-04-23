// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditFilterSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
