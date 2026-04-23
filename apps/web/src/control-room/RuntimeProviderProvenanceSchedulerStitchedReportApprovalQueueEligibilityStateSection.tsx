// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueEligibilityStateSection({
  model,
  plan,
  mutation,
  children,
}: {
  model: any;
  plan: any;
  mutation: "approve" | "apply" | "rollback";
  children: any;
}) {
  const { providerProvenanceSchedulerNarrativeGovernancePlanAction } = model;

  const disabled =
    (mutation === "approve" && plan.status !== "previewed")
    || (mutation === "apply" && plan.status !== "approved")
    || (mutation === "rollback" && plan.status !== "applied")
    || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null;

  return children(disabled);
}
