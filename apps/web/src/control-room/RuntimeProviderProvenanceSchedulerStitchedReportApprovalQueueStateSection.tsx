// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSummarySection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSummarySection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueAsyncStateSection model={model} />
    </>
  );
}
