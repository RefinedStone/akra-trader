// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePlanOriginSummarySection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <p className="run-lineage-symbol-copy">
      {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} ·{" "}
      {formatTimestamp(plan.updated_at)}
    </p>
  );
}
