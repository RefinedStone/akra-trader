// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCountSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCountSummarySection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewHeadlineSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewHeadlineSummarySection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueRollbackSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueRollbackSummarySection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCellSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <td>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewHeadlineSummarySection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueRollbackSummarySection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCountSummarySection
        model={model}
        plan={plan}
      />
    </td>
  );
}
