// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection({
  entry,
  model,
}: {
  entry: any;
  model: any;
}) {
  const {
    formatTimestamp,
    formatWorkflowToken,
    providerProvenanceSchedulerNarrativeTemplateNameMap,
  } = model;

  return (
    <>
      <td>
        <strong>{entry.name}</strong>
        <p className="run-lineage-symbol-copy">
          {entry.filter_summary}
        </p>
        <p className="run-lineage-symbol-copy">
          {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
        </p>
      </td>
      <td>
        <strong>{providerProvenanceSchedulerNarrativeTemplateNameMap.get(entry.template_id ?? "") ?? "No template link"}</strong>
        <p className="run-lineage-symbol-copy">
          Highlight {entry.layout.highlight_panel} · {entry.focus.symbol ?? "all symbols"} · {entry.focus.timeframe ?? "all windows"}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s) · updated {formatTimestamp(entry.updated_at)}
        </p>
      </td>
    </>
  );
}
