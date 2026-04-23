// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection
        model={model}
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection
        model={model}
        plan={plan}
      />
    </>
  );
}
