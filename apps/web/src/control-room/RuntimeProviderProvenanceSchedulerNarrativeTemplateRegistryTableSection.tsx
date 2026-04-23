// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return providerProvenanceSchedulerNarrativeTemplates.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th>
            <input
              aria-label="Select all scheduler narrative templates"
              checked={
                providerProvenanceSchedulerNarrativeTemplates.length > 0
                && selectedProviderProvenanceSchedulerNarrativeTemplateIds.length === providerProvenanceSchedulerNarrativeTemplates.length
              }
              onChange={toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections}
              type="checkbox"
            />
          </th>
          <th>Template</th>
          <th>Lens</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
          <tr key={entry.template_id}>
            <td className="provider-provenance-selection-cell">
              <input
                aria-label={`Select scheduler narrative template ${entry.name}`}
                checked={selectedProviderProvenanceSchedulerNarrativeTemplateIdSet.has(entry.template_id)}
                onChange={() => {
                  toggleProviderProvenanceSchedulerNarrativeTemplateSelection(entry.template_id);
                }}
                type="checkbox"
              />
            </td>
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
            <td>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={entry.status !== "active"}
                  onClick={() => {
                    setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                      ...current,
                      template_id: entry.template_id,
                    }));
                    void applyProviderProvenanceWorkspaceQuery(entry, {
                      includeLayout: false,
                      forceSchedulerHighlight: true,
                      feedbackLabel: `Scheduler template ${entry.name}`,
                    });
                  }}
                  type="button"
                >
                  Apply
                </button>
                <button
                  className="ghost-button"
                  disabled={providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                  onClick={() => {
                    void editProviderProvenanceSchedulerNarrativeTemplate(entry);
                  }}
                  type="button"
                >
                  Edit
                </button>
                <button
                  className="ghost-button"
                  disabled={entry.status !== "active" || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                  onClick={() => {
                    void removeProviderProvenanceSchedulerNarrativeTemplate(entry);
                  }}
                  type="button"
                >
                  Delete
                </button>
                <button
                  className="ghost-button"
                  disabled={providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                  onClick={() => {
                    void toggleProviderProvenanceSchedulerNarrativeTemplateHistory(entry.template_id);
                  }}
                  type="button"
                >
                  {selectedProviderProvenanceSchedulerNarrativeTemplateId === entry.template_id
                    && selectedProviderProvenanceSchedulerNarrativeTemplateHistory
                    ? "Hide versions"
                    : "Versions"}
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  ) : (
    <p className="empty-state">No scheduler narrative templates saved yet.</p>
  );
}
