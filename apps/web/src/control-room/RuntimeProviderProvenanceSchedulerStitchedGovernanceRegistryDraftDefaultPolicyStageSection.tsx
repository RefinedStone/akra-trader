// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftDefaultPolicyStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Default policy template</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
              ...current,
              default_policy_template_id: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.default_policy_template_id}
        >
          <option value="">No default policy template</option>
          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
            .filter((entry) =>
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "stitched_report_view",
              ),
            )
            .map((entry) => (
              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                {entry.name}
              </option>
            ))}
        </select>
      </label>
      <label>
        <span>Default policy catalog</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
              ...current,
              default_policy_catalog_id: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.default_policy_catalog_id}
        >
          <option value="">No default policy catalog</option>
          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
            <option key={entry.catalog_id} value={entry.catalog_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
    </>
  );
}
