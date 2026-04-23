// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
