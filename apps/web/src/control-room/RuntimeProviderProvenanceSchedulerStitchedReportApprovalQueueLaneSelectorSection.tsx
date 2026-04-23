// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneSelectorSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
