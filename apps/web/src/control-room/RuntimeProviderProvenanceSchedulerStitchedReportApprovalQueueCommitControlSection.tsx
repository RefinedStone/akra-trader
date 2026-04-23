// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateLeafSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateLeafSection";

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
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateLeafSection
        model={model}
        mutation="approve"
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateLeafSection
        model={model}
        mutation="apply"
        plan={plan}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateLeafSection
        model={model}
        mutation="rollback"
        plan={plan}
      />
    </>
  );
}
