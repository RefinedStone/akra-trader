// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionDispatchFlowSection({
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
  const {
    approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry,
    applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry,
    rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry,
  } = model;

  const handleClick = () => {
    if (mutation === "approve") {
      void approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
      return;
    }
    if (mutation === "apply") {
      void applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
      return;
    }
    void rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
  };

  return children({ handleClick });
}
