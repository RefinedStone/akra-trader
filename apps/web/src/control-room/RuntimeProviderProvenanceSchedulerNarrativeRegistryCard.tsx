// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkGovernanceSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkGovernanceSection";
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionHistorySection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionHistorySection";
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryTableSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryTableSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryCard({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Scheduler narrative registry</strong>
        <p>Store a named shared review board for occurrence narratives with an optional template link.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Lag recovery board"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="shared scheduler occurrence board"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryDraft.description}
          />
        </label>
        <label>
          <span>Template</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                ...current,
                template_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryDraft.template_id}
          >
            <option value="">No template link</option>
            {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
              <option key={entry.template_id} value={entry.template_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveCurrentProviderProvenanceSchedulerNarrativeRegistryEntry();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerNarrativeRegistryId ? "Save changes" : "Save registry"}
            </button>
            {editingProviderProvenanceSchedulerNarrativeRegistryId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerNarrativeRegistryDraft();
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
        </label>
      </div>
      <RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkGovernanceSection model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeRegistryTableSection model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionHistorySection model={model} />
    </div>
  );
}
