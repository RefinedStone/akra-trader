// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkPatchStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="filter-bar">
      <label>
        <span>Bulk query patch</span>
        <textarea
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              query_patch: event.target.value,
            }))
          }
          placeholder='{"scheduler_alert_status":"resolved"}'
          rows={3}
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.query_patch}
        />
      </label>
      <label>
        <span>Bulk layout patch</span>
        <textarea
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
              ...current,
              layout_patch: event.target.value,
            }))
          }
          placeholder='{"show_recent_exports":true}'
          rows={3}
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.layout_patch}
        />
      </label>
    </div>
  );
}
