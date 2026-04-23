// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanIdentitySummarySection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <>
      <strong>{formatWorkflowToken(plan.action)} stitched_report_view</strong>
      <p className="run-lineage-symbol-copy">
        {shortenIdentifier(plan.plan_id, 10)} ·{" "}
        {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
      </p>
    </>
  );
}
