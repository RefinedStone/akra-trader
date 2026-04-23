// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryTableViewSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
            <RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection entry={entry} />
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
  );
}
