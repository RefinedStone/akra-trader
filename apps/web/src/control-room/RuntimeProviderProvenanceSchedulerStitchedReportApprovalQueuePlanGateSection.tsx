// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionLeafSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionLeafSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueEligibilityStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueEligibilityStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLabelPolicySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLabelPolicySection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection({
  model,
  plan,
  mutation,
}: {
  model: any;
  plan: any;
  mutation: "approve" | "apply" | "rollback";
}) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueEligibilityStateSection
      model={model}
      mutation={mutation}
      plan={plan}
    >
      {(disabled: boolean) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLabelPolicySection
          model={model}
          mutation={mutation}
        >
          {(label: string) => (
            <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionLeafSection
              disabled={disabled}
              label={label}
              model={model}
              mutation={mutation}
              plan={plan}
            />
          )}
        </RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLabelPolicySection>
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueEligibilityStateSection>
  );
}
