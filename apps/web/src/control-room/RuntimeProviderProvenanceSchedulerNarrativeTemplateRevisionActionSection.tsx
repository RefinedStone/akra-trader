// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionActionSection({
  entry,
  model,
}: {
  entry: any;
  model: any;
}) {
  const {
    applyProviderProvenanceWorkspaceQuery,
    restoreProviderProvenanceSchedulerNarrativeTemplateHistoryRevision,
  } = model;

  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            void applyProviderProvenanceWorkspaceQuery(entry, {
              includeLayout: false,
              forceSchedulerHighlight: true,
              feedbackLabel: `Template revision ${entry.revision_id}`,
            });
          }}
          type="button"
        >
          Apply snapshot
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void restoreProviderProvenanceSchedulerNarrativeTemplateHistoryRevision(entry);
          }}
          type="button"
        >
          Restore revision
        </button>
      </div>
    </td>
  );
}
