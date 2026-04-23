// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateLeafSection({
  model,
  plan,
  mutation,
}: {
  model: any;
  plan: any;
  mutation: "approve" | "apply" | "rollback";
}) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection
      model={model}
      mutation={mutation}
      plan={plan}
    />
  );
}
