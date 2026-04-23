// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <label>
        <span>Queue state</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              queue_state: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.queue_state}
        >
          <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
          <option value={ALL_FILTER_VALUE}>All queue states</option>
          <option value="pending_approval">pending approval</option>
          <option value="ready_to_apply">ready to apply</option>
          <option value="completed">completed</option>
        </select>
      </label>
      <label>
        <span>Lane</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              approval_lane: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.approval_lane}
        >
          <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
          <option value={ALL_FILTER_VALUE}>Clear lane</option>
          <option value="chatops">chatops</option>
          <option value="ops">ops</option>
          <option value="leadership">leadership</option>
        </select>
      </label>
      <label>
        <span>Priority</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              approval_priority: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.approval_priority}
        >
          <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
          <option value={ALL_FILTER_VALUE}>Clear priority</option>
          <option value="low">low</option>
          <option value="normal">normal</option>
          <option value="high">high</option>
          <option value="critical">critical</option>
        </select>
      </label>
      <label>
        <span>Search</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              search: event.target.value,
            }))
          }
          placeholder="keep current or blank to clear"
          type="text"
          value={
            providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.search
            === KEEP_CURRENT_BULK_GOVERNANCE_VALUE
              ? ""
              : providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.search
          }
        />
      </label>
      <label>
        <span>Sort</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              sort: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.sort}
        >
          <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
          <option value={ALL_FILTER_VALUE}>Clear sort</option>
          <option value="queue_priority">queue priority</option>
          <option value="updated_desc">updated newest</option>
          <option value="updated_asc">updated oldest</option>
          <option value="created_desc">created newest</option>
          <option value="created_asc">created oldest</option>
        </select>
      </label>
    </>
  );
}
