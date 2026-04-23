// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterBarSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterBarSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterBarSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection model={model} />
    </>
  );
}
