// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkMetadataStageSection({
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
      <label>
        <span>Default template</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
              ...current,
              default_policy_template_id: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.default_policy_template_id}
        >
          <option value="">Keep current default</option>
          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
            .filter((entry) => entry.status === "active")
            .map((entry) => (
              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                {entry.name}
              </option>
            ))}
        </select>
      </label>
    </>
  );
}
