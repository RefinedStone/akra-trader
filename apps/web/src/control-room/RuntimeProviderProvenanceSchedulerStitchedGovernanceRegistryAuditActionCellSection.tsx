// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{formatWorkflowToken(entry.action)}</strong>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(entry.status)} ·{" "}
        {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
          entry.queue_view,
        ) ?? "All stitched governance plans"}
      </p>
    </td>
  );
}
