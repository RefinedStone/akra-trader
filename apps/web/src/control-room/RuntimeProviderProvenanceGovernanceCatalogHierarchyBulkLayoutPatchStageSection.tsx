// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkLayoutPatchStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
