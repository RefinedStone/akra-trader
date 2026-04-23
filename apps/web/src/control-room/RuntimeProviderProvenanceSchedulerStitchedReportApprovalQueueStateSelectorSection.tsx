// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateOptionSourceSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateOptionSourceSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSelectorSection({ model }: { model: any }) {
  const {} = model;

  return (
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
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateOptionSourceSection model={model} />
      </select>
    </label>
  );
}
