// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionDispatchFlowSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionDispatchFlowSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionMutationTriggerSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionMutationTriggerSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection({
  model,
  plan,
  mutation,
  disabled,
  label,
}: {
  model: any;
  plan: any;
  mutation: "approve" | "apply" | "rollback";
  disabled: boolean;
  label: string;
}) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionDispatchFlowSection
      model={model}
      mutation={mutation}
      plan={plan}
    >
      {({ handleClick }: { handleClick: () => void }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionMutationTriggerSection
          disabled={disabled}
          label={label}
          onClick={handleClick}
        />
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionDispatchFlowSection>
  );
}
