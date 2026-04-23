// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneOptionSourceSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneOptionSourceSection";

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
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneOptionSourceSection model={model} />
      </select>
    </label>
  );
}
