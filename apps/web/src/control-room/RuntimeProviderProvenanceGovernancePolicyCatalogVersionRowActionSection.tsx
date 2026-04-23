// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowActionSection({
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
            setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId(
              entry.catalog_id,
            );
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft({
              name: entry.name,
              description: entry.description,
              default_policy_template_id: entry.default_policy_template_id ?? "",
            });
            setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds(
              entry.policy_template_ids,
            );
            setProviderProvenanceWorkspaceFeedback(
              `Policy catalog revision ${entry.revision_id} staged in the editor.`,
            );
          }}
          type="button"
        >
          Stage draft
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryRevision(
              entry,
            );
          }}
          type="button"
        >
          Restore revision
        </button>
      </div>
    </td>
  );
}
