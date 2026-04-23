// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkDefaultTemplateStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
