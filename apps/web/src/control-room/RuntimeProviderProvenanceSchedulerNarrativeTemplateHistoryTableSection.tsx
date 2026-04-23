// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionActionSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionActionSection";

export function RuntimeProviderProvenanceSchedulerNarrativeTemplateHistoryTableSection({
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
        {selectedProviderProvenanceSchedulerNarrativeTemplateHistory.history.map((entry) => (
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
              <p className="run-lineage-symbol-copy">{entry.reason}</p>
            </td>
            <RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
