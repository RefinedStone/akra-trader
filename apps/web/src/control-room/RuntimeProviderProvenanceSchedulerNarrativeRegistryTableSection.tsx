// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (providerProvenanceSchedulerNarrativeRegistryEntriesLoading) {
    return <p className="empty-state">Loading scheduler narrative registry…</p>;
  }

  if (providerProvenanceSchedulerNarrativeRegistryEntriesError) {
    return (
      <p className="market-data-workflow-feedback">
        Scheduler narrative registry load failed: {providerProvenanceSchedulerNarrativeRegistryEntriesError}
      </p>
    );
  }

  return providerProvenanceSchedulerNarrativeRegistryEntries.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th>
            <input
              aria-label="Select all scheduler narrative registry entries"
              checked={
                providerProvenanceSchedulerNarrativeRegistryEntries.length > 0
                && selectedProviderProvenanceSchedulerNarrativeRegistryIds.length === providerProvenanceSchedulerNarrativeRegistryEntries.length
              }
              onChange={toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections}
              type="checkbox"
            />
          </th>
          <th>Registry</th>
          <th>Linked lens</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerNarrativeRegistryEntries.map((entry) => (
          <tr key={entry.registry_id}>
            <td className="provider-provenance-selection-cell">
              <input
                aria-label={`Select scheduler narrative registry ${entry.name}`}
                checked={selectedProviderProvenanceSchedulerNarrativeRegistryIdSet.has(entry.registry_id)}
                onChange={() => {
                  toggleProviderProvenanceSchedulerNarrativeRegistrySelection(entry.registry_id);
                }}
                type="checkbox"
              />
            </td>
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
            <td>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={entry.status !== "active"}
                  onClick={() => {
                    setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                      ...current,
                      template_id: entry.template_id ?? "",
                    }));
                    void applyProviderProvenanceWorkspaceQuery(entry, {
                      includeLayout: true,
                      feedbackLabel: `Narrative registry ${entry.name}`,
                    });
                  }}
                  type="button"
                >
                  Apply
                </button>
                <button
                  className="ghost-button"
                  disabled={providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                  onClick={() => {
                    void editProviderProvenanceSchedulerNarrativeRegistryEntry(entry);
                  }}
                  type="button"
                >
                  Edit
                </button>
                <button
                  className="ghost-button"
                  disabled={entry.status !== "active" || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                  onClick={() => {
                    void removeProviderProvenanceSchedulerNarrativeRegistry(entry);
                  }}
                  type="button"
                >
                  Delete
                </button>
                <button
                  className="ghost-button"
                  disabled={providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                  onClick={() => {
                    void toggleProviderProvenanceSchedulerNarrativeRegistryHistory(entry.registry_id);
                  }}
                  type="button"
                >
                  {selectedProviderProvenanceSchedulerNarrativeRegistryId === entry.registry_id
                    && selectedProviderProvenanceSchedulerNarrativeRegistryHistory
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
    <p className="empty-state">No scheduler narrative registry entries saved yet.</p>
  );
}
