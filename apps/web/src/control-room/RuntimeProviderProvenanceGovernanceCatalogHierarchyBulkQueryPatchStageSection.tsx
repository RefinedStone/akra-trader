// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkQueryPatchStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
