// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePriorityOptionSourceSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePriorityOptionSourceSection";

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
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePriorityOptionSourceSection model={model} />
      </select>
    </label>
  );
}
