// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSearchSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Search</span>
      <input
        onChange={(event) => {
          setProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch(
            event.target.value,
          );
        }}
        placeholder="catalog, guidance, registry policy"
        type="text"
        value={providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch}
      />
    </label>
  );
}
