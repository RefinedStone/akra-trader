// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueFilterPolicySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Policy template</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
              ...current,
              policy_template_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.policy_template_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy templates</option>
          <option value="">No policy template</option>
          {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
            <option key={entry.policy_template_id} value={entry.policy_template_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Policy catalog</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
              ...current,
              policy_catalog_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.policy_catalog_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
          <option value="">No policy catalog</option>
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.map((entry) => (
            <option key={entry.catalog_id} value={entry.catalog_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
    </>
  );
}
