// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterBarSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="filter-bar">
      <label>
        <span>Queue state</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              queue_state:
                event.target.value === "pending_approval"
                || event.target.value === "ready_to_apply"
                || event.target.value === "completed"
                  ? event.target.value
                  : ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.queue_state}
        >
          <option value={ALL_FILTER_VALUE}>All states</option>
          <option value="pending_approval">Pending approval</option>
          <option value="ready_to_apply">Ready to apply</option>
          <option value="completed">Completed</option>
        </select>
      </label>
      <label>
        <span>Lane</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              approval_lane: event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.approval_lane}
        >
          <option value={ALL_FILTER_VALUE}>All lanes</option>
          {Array.from(
            new Set(
              providerProvenanceSchedulerStitchedReportGovernancePlans.map(
                (entry) => entry.approval_lane,
              ),
            ),
          ).sort().map((lane) => (
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
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              approval_priority: event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.approval_priority}
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
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              policy_template_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_template_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy templates</option>
          <option value="">No policy template</option>
          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
            .filter((entry) =>
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "stitched_report_view",
              ),
            )
            .map((entry) => (
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
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              policy_catalog_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_catalog_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
          <option value="">No policy catalog</option>
          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
            <option key={entry.catalog_id} value={entry.catalog_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Search</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              search: event.target.value,
            }))
          }
          placeholder="plan, view, policy"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.search}
        />
      </label>
      <label>
        <span>Sort</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                event.target.value,
              ),
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.sort}
        >
          <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
            Queue priority
          </option>
          <option value="updated_desc">Updated newest</option>
          <option value="updated_asc">Updated oldest</option>
          <option value="created_desc">Created newest</option>
          <option value="created_asc">Created oldest</option>
        </select>
      </label>
    </div>
  );
}
