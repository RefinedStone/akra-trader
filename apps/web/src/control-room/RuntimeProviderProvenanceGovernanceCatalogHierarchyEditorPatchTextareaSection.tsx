// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorPatchTextareaSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
