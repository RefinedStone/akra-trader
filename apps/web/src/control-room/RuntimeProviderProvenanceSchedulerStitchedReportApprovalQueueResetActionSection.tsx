// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
