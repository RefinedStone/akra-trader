// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportGovernancePlans.map((plan) => (
        <tr key={`provider-scheduler-stitched-governance-plan-${plan.plan_id}`}>
          <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection
            model={model}
            plan={plan}
          />
          <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection
            model={model}
            plan={plan}
          />
        </tr>
      ))}
    </>
  );
}
