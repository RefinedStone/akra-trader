// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection({
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
      <p className="run-lineage-symbol-copy">{entry.name}</p>
    </td>
  );
}
