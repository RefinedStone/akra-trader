// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryRowDetailSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryRowDetailSection";

export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableViewSection({
  model,
}: {
  model: any;
}) {
  const {
    applyProviderProvenanceWorkspaceQuery,
    editProviderProvenanceSchedulerNarrativeTemplate,
    providerProvenanceSchedulerNarrativeTemplateBulkAction,
    providerProvenanceSchedulerNarrativeTemplates,
    removeProviderProvenanceSchedulerNarrativeTemplate,
    selectedProviderProvenanceSchedulerNarrativeTemplateHistory,
    selectedProviderProvenanceSchedulerNarrativeTemplateId,
    selectedProviderProvenanceSchedulerNarrativeTemplateIds,
    selectedProviderProvenanceSchedulerNarrativeTemplateIdSet,
    setProviderProvenanceSchedulerNarrativeRegistryDraft,
    toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections,
    toggleProviderProvenanceSchedulerNarrativeTemplateHistory,
    toggleProviderProvenanceSchedulerNarrativeTemplateSelection,
  } = model;

  return (
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
            <RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryRowDetailSection entry={entry} model={model} />
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
  );
}
