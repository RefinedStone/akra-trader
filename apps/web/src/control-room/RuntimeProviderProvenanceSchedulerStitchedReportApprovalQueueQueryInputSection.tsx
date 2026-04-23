// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueryInputSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
