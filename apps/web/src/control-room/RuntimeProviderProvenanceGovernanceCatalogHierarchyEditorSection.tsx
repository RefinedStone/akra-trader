// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Hierarchy step editor</strong>
        <p>Edit one captured step directly. Empty JSON clears the current patch.</p>
      </div>
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
        <div className="filter-bar">
          <label>
            <span>Targets</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                  ...current,
                  item_ids_text: event.target.value,
                }))
              }
              placeholder="id_1, id_2"
              type="text"
              value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.item_ids_text}
            />
          </label>
          <label>
            <span>Name prefix</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                  ...current,
                  name_prefix: event.target.value,
                }))
              }
              placeholder="Reviewed / "
              type="text"
              value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.name_prefix}
            />
          </label>
          <label>
            <span>Name suffix</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                  ...current,
                  name_suffix: event.target.value,
                }))
              }
              placeholder=" / approved"
              type="text"
              value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.name_suffix}
            />
          </label>
          <label>
            <span>Description</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                  ...current,
                  description_append: event.target.value,
                }))
              }
              placeholder="shared governance note"
              type="text"
              value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.description_append}
            />
          </label>
          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep.item_type === "registry" ? (
            <>
              <label>
                <span>Template link</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                      ...current,
                      template_id: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.template_id}
                >
                  <option value="">No explicit template link</option>
                  {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                    <option key={entry.template_id} value={entry.template_id}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Clear link</span>
                <input
                  checked={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.clear_template_link}
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                      ...current,
                      clear_template_link: event.target.checked,
                    }))
                  }
                  type="checkbox"
                />
              </label>
            </>
          ) : null}
          <label>
            <span>Action</span>
            <button
              className="ghost-button"
              onClick={() => {
                void saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep();
              }}
              type="button"
            >
              Save step
            </button>
          </label>
          <label>
            <span>Action</span>
            <button
              className="ghost-button"
              onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft}
              type="button"
            >
              Clear draft
            </button>
          </label>
        </div>
      ) : (
        <p className="empty-state">Select a hierarchy step row and choose Edit to stage it in the editor.</p>
      )}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
        <div className="filter-bar">
          <label>
            <span>Query patch</span>
            <textarea
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                  ...current,
                  query_patch: event.target.value,
                }))
              }
              placeholder='{"scheduler_alert_status":"resolved"}'
              rows={4}
              value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.query_patch}
            />
          </label>
          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep.item_type === "registry" ? (
            <label>
              <span>Layout patch</span>
              <textarea
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                    ...current,
                    layout_patch: event.target.value,
                  }))
                }
                placeholder='{"show_recent_exports":true}'
                rows={4}
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.layout_patch}
              />
            </label>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
