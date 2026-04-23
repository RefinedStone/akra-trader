// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitControlSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection
        model={model}
        mutation="approve"
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection
        model={model}
        mutation="apply"
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection
        model={model}
        mutation="rollback"
        plan={plan}
      />
    </>
  );
}
