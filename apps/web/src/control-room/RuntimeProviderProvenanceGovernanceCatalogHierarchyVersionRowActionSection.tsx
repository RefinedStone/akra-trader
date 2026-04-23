// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowActionSection({
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
            stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft(entry.step);
          }}
          type="button"
        >
          Stage draft
        </button>
        <button
          className="ghost-button"
          disabled={!entry.step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
          onClick={() => {
            void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersion(entry);
          }}
          type="button"
        >
          Restore step
        </button>
      </div>
    </td>
  );
}
