// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePreviewCountSummarySection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <p className="run-lineage-symbol-copy">
      {plan.preview_items.length} preview row(s) · rollback ready{" "}
      {plan.rollback_ready_count}
    </p>
  );
}
