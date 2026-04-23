// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionActionSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionActionSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryHistoryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>When</th>
          <th>Snapshot</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeRegistryHistory.history.map((entry) => (
          <tr key={entry.revision_id}>
            <td>
              <strong>{formatTimestamp(entry.recorded_at)}</strong>
              <p className="run-lineage-symbol-copy">
                {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
              </p>
            </td>
            <td>
              <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
              <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
              <p className="run-lineage-symbol-copy">
                {providerProvenanceSchedulerNarrativeTemplateNameMap.get(entry.template_id ?? "") ?? "No template link"} · highlight {entry.layout.highlight_panel}
              </p>
              <p className="run-lineage-symbol-copy">{entry.reason}</p>
            </td>
            <RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
