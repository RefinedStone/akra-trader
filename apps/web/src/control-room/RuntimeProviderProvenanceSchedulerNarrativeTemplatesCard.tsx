// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkGovernanceSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkGovernanceSection";
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableSection";
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionHistorySection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionHistorySection";

export function RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard({
  model,
}: {
  model: any;
}) {
  const {
    editingProviderProvenanceSchedulerNarrativeTemplateId,
    providerProvenanceSchedulerNarrativeTemplateDraft,
    providerProvenanceSchedulerNarrativeTemplatesError,
    providerProvenanceSchedulerNarrativeTemplatesLoading,
    resetProviderProvenanceSchedulerNarrativeTemplateDraft,
    saveCurrentProviderProvenanceSchedulerNarrativeTemplate,
    setProviderProvenanceSchedulerNarrativeTemplateDraft,
  } = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Scheduler narrative templates</strong>
        <p>Save reusable occurrence lenses that only carry the scheduler narrative query state.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Resolved lag recovery"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="resolved scheduler narrative lens"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateDraft.description}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveCurrentProviderProvenanceSchedulerNarrativeTemplate();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerNarrativeTemplateId ? "Save changes" : "Save template"}
            </button>
            {editingProviderProvenanceSchedulerNarrativeTemplateId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerNarrativeTemplateDraft();
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
        </label>
      </div>
      <RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkGovernanceSection model={model} />
      {providerProvenanceSchedulerNarrativeTemplatesLoading ? (
        <p className="empty-state">Loading scheduler narrative templates…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplatesError ? (
        <p className="market-data-workflow-feedback">
          Scheduler narrative template registry load failed: {providerProvenanceSchedulerNarrativeTemplatesError}
        </p>
      ) : null}
      <RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableSection model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionHistorySection model={model} />
    </div>
  );
}
