// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyCatalogSelectorSection({ model }: { model: any }) {
  const {} = model;

  return (
    <label>
      <span>Policy catalog</span>
      <select
        onChange={(event) =>
          setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
            ...current,
            policy_catalog_id:
              event.target.value === ""
                ? ""
                : event.target.value || ALL_FILTER_VALUE,
          }))
        }
        value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_catalog_id}
      >
        <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
        <option value="">No policy catalog</option>
        {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
          <option key={entry.catalog_id} value={entry.catalog_id}>
            {entry.name}
          </option>
        ))}
      </select>
    </label>
  );
}
