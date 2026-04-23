// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueuePreviewDetailSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
      <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
      <p className="run-lineage-symbol-copy">
        {plan.preview_items.length} preview row(s) · rollback ready {plan.rollback_ready_count}
      </p>
    </td>
  );
}
