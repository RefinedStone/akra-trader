// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLabelPolicySection({
  model,
  mutation,
  children,
}: {
  model: any;
  mutation: "approve" | "apply" | "rollback";
  children: any;
}) {
  const { providerProvenanceSchedulerNarrativeGovernancePlanAction } = model;

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

  return children(label);
}
