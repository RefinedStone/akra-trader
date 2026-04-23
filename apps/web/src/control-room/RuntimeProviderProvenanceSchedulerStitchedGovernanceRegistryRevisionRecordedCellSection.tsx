// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{formatTimestamp(entry.recorded_at)}</strong>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}
      </p>
      <p className="run-lineage-symbol-copy">
        {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
      </p>
    </td>
  );
}
