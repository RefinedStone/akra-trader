// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionLeafSection({
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
    <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection
      disabled={disabled}
      label={label}
      model={model}
      mutation={mutation}
      plan={plan}
    />
  );
}
