// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogActionSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={catalog.status !== "active"}
          onClick={() => {
            applyProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalog(catalog);
          }}
          type="button"
        >
          Use defaults
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(catalog);
          }}
          type="button"
        >
          Open shared catalog
        </button>
      </div>
    </td>
  );
}
