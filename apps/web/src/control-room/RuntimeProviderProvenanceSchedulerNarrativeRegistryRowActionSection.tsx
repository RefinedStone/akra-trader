// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryRowActionSection({
  entry,
  model,
}: {
  entry: any;
  model: any;
}) {
  const {
    applyProviderProvenanceWorkspaceQuery,
    editProviderProvenanceSchedulerNarrativeRegistryEntry,
    providerProvenanceSchedulerNarrativeRegistryBulkAction,
    removeProviderProvenanceSchedulerNarrativeRegistry,
    selectedProviderProvenanceSchedulerNarrativeRegistryHistory,
    selectedProviderProvenanceSchedulerNarrativeRegistryId,
    setProviderProvenanceSchedulerNarrativeRegistryDraft,
    toggleProviderProvenanceSchedulerNarrativeRegistryHistory,
  } = model;

  return (
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
          disabled={
            entry.status !== "active" ||
            providerProvenanceSchedulerNarrativeRegistryBulkAction !== null
          }
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
          {selectedProviderProvenanceSchedulerNarrativeRegistryId === entry.registry_id &&
          selectedProviderProvenanceSchedulerNarrativeRegistryHistory
            ? "Hide versions"
            : "Versions"}
        </button>
      </div>
    </td>
  );
}
