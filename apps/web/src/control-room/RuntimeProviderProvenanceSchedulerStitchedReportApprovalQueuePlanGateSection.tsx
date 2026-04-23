// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanGateSection({
  model,
  plan,
  mutation,
}: {
  model: any;
  plan: any;
  mutation: "approve" | "apply" | "rollback";
}) {
  const {} = model;

  const disabled =
    (mutation === "approve" && plan.status !== "previewed")
    || (mutation === "apply" && plan.status !== "approved")
    || (mutation === "rollback" && plan.status !== "applied")
    || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null;

  const label =
    mutation === "approve"
      ? providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
        ? "Approving…"
        : "Approve"
      : mutation === "apply"
        ? providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
          ? "Applying…"
          : "Apply"
        : providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
          ? "Rolling back…"
          : "Rollback";

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
