// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryRowDetailSection({
  entry,
  model,
}: {
  entry: any;
  model: any;
}) {
  const { formatTimestamp, formatWorkflowToken } = model;

  return (
    <>
      <td>
        <strong>{entry.name}</strong>
        <p className="run-lineage-symbol-copy">
          {entry.focus.symbol ?? "all symbols"} · {entry.focus.timeframe ?? "all windows"}
        </p>
        <p className="run-lineage-symbol-copy">
          {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
        </p>
      </td>
      <td>
        <strong>{entry.filter_summary}</strong>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
        </p>
        <p className="run-lineage-symbol-copy">
          Updated {formatTimestamp(entry.updated_at)}{entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
        </p>
      </td>
    </>
  );
}
