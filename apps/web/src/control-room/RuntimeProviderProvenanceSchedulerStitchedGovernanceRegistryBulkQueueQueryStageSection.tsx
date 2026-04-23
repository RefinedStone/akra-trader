// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkQueueQueryStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
