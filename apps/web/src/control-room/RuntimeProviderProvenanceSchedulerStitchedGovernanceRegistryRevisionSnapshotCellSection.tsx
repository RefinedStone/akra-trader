// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{entry.name}</strong>
      <p className="run-lineage-symbol-copy">{entry.description || "No description recorded."}</p>
      <p className="run-lineage-symbol-copy">
        {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
          entry.queue_view,
        ) ?? "All stitched governance plans"}
      </p>
      <p className="run-lineage-symbol-copy">
        {entry.default_policy_template_name ?? "No default policy template"}
        {entry.default_policy_catalog_name
          ? ` · ${entry.default_policy_catalog_name}`
          : ""}
      </p>
    </td>
  );
}
