// @ts-nocheck
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
  const {} = model;

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

  return (
    <button
      className="ghost-button"
      disabled={disabled}
      onClick={handleClick}
      type="button"
    >
      {label}
    </button>
  );
}
