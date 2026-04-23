// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection({
  model,
  children,
}: {
  model: any;
  children: (entries: any[]) => any;
}) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading ? (
        <p className="empty-state">Loading stitched governance registries…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportGovernanceRegistriesError ? (
        <p className="market-data-workflow-feedback">
          Stitched governance registries failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistriesError}
        </p>
      ) : null}
      {filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
        children(filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries)
      ) : (
        !providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading
          ? <p className="empty-state">No stitched governance registries match the current search.</p>
          : null
      )}
    </>
  );
}
