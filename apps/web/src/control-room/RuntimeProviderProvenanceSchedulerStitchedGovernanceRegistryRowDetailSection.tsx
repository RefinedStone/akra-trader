// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowDetailSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <>
      <td>
        <strong>{entry.name}</strong>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(entry.status)} · revisions {entry.revision_count}
        </p>
        <p className="run-lineage-symbol-copy">
          {entry.description || "No stitched governance registry description recorded."}
        </p>
        <p className="run-lineage-symbol-copy">
          {entry.default_policy_template_name ?? "No default policy template"}
          {entry.default_policy_catalog_name
            ? ` · ${entry.default_policy_catalog_name}`
            : ""}
        </p>
      </td>
      <td>
        <strong>
          {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
            entry.queue_view,
          ) ?? "All stitched governance plans"}
        </strong>
        <p className="run-lineage-symbol-copy">
          Saved {formatTimestamp(entry.updated_at)}
        </p>
        <p className="run-lineage-symbol-copy">
          {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
        </p>
      </td>
    </>
  );
}
