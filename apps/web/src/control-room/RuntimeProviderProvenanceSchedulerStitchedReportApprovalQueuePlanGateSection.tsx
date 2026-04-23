// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection";
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
            <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection
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
