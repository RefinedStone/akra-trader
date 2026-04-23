// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionActionSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            void applyProviderProvenanceWorkspaceQuery(entry, {
              includeLayout: true,
              feedbackLabel: `Registry revision ${entry.revision_id}`,
            });
          }}
          type="button"
        >
          Apply snapshot
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void restoreProviderProvenanceSchedulerNarrativeRegistryHistoryRevision(entry);
          }}
          type="button"
        >
          Restore revision
        </button>
      </div>
    </td>
  );
}
