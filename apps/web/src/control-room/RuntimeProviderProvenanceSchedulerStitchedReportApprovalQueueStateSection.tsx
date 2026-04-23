// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSummarySection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSummarySection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection model={model} />
    </>
  );
}
