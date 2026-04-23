// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePrioritySelectorSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
