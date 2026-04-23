// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkNameStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Name prefix</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
              ...current,
              name_prefix: event.target.value,
            }))
          }
          placeholder="Shift "
          type="text"
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.name_prefix}
        />
      </label>
      <label>
        <span>Name suffix</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
              ...current,
              name_suffix: event.target.value,
            }))
          }
          placeholder=" / archived"
          type="text"
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.name_suffix}
        />
      </label>
    </>
  );
}
