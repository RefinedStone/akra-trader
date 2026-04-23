// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanApprovalSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanApprovalSummarySection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanIdentitySummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanIdentitySummarySection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanOriginSummarySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanOriginSummarySection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanCellSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <td>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanIdentitySummarySection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanOriginSummarySection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanApprovalSummarySection
        model={model}
        plan={plan}
      />
    </td>
  );
}
