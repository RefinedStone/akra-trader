// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkDescriptionStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Description append</span>
      <input
        onChange={(event) =>
          setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
            ...current,
            description_append: event.target.value,
          }))
        }
        placeholder="requires desk review"
        type="text"
        value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.description_append}
      />
    </label>
  );
}
