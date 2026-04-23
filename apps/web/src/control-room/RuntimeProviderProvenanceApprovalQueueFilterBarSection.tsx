// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueFilterBarSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="filter-bar">
      <label>
        <span>Queue state</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              queue_state:
                event.target.value === "pending_approval"
                || event.target.value === "ready_to_apply"
                || event.target.value === "completed"
                  ? event.target.value
                  : ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.queue_state}
        >
          <option value={ALL_FILTER_VALUE}>All queue states</option>
          <option value="pending_approval">Pending approval</option>
          <option value="ready_to_apply">Ready to apply</option>
          <option value="completed">Completed</option>
        </select>
      </label>
      <label>
        <span>Item type</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              item_type:
                event.target.value === "template"
                || event.target.value === "registry"
                || event.target.value === "stitched_report_view"
                || event.target.value === "stitched_report_governance_registry"
                  ? event.target.value
                  : ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.item_type}
        >
          <option value={ALL_FILTER_VALUE}>All item types</option>
          <option value="template">Templates</option>
          <option value="registry">Registry</option>
          <option value="stitched_report_view">Stitched report views</option>
          <option value="stitched_report_governance_registry">Stitched governance registries</option>
        </select>
      </label>
      <label>
        <span>Lane</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              approval_lane: event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.approval_lane}
        >
          <option value={ALL_FILTER_VALUE}>All lanes</option>
          {Array.from(new Set(providerProvenanceSchedulerNarrativeGovernancePlans.map((entry) => entry.approval_lane))).sort().map((lane) => (
            <option key={lane} value={lane}>
              {formatWorkflowToken(lane)}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Priority</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              approval_priority: event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.approval_priority}
        >
          <option value={ALL_FILTER_VALUE}>All priorities</option>
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </label>
      <label>
        <span>Policy template</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              policy_template_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.policy_template_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy templates</option>
          <option value="">No policy template</option>
          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
            <option key={entry.policy_template_id} value={entry.policy_template_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Policy catalog</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              policy_catalog_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.policy_catalog_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
          <option value="">No policy catalog</option>
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((entry) => (
            <option key={entry.catalog_id} value={entry.catalog_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Source template</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              source_hierarchy_step_template_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.source_hierarchy_step_template_id}
        >
          <option value={ALL_FILTER_VALUE}>All source templates</option>
          <option value="">No source template</option>
          {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
            <option key={entry.hierarchy_step_template_id} value={entry.hierarchy_step_template_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Search</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              search: event.target.value,
            }))
          }
          placeholder="plan, template, hierarchy"
          type="text"
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.search}
        />
      </label>
      <label>
        <span>Sort</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
              ...current,
              sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                event.target.value,
              ),
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.sort}
        >
          <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
            Queue priority
          </option>
          <option value="updated_desc">Updated newest</option>
          <option value="updated_asc">Updated oldest</option>
          <option value="created_desc">Created newest</option>
          <option value="created_asc">Created oldest</option>
          <option value="source_template_asc">Source template A-Z</option>
          <option value="source_template_desc">Source template Z-A</option>
        </select>
      </label>
    </div>
  );
}
