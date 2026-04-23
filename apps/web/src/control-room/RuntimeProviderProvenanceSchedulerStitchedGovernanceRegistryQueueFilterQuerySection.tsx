// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterQuerySection({
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
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
              ...current,
              search: event.target.value,
            }))
          }
          placeholder="plan, registry, policy"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.search}
        />
      </label>
      <label>
        <span>Sort</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
              ...current,
              sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                event.target.value,
              ),
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.sort}
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
    </>
  );
}
