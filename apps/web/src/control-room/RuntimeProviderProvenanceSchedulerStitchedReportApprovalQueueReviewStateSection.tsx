// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCellSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanCellSection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCellSection
        model={model}
        plan={plan}
      />
    </>
  );
}
