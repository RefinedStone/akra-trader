// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowActionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowActionSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowDetailSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowDetailSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogRegistryTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsLoading ? (
        <p className="empty-state">Loading governance policy catalogs…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError ? (
        <p className="market-data-workflow-feedback">
          Governance policy catalog load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th aria-label="Select catalog">Sel</th>
              <th>Catalog</th>
              <th>Defaults</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((catalog) => (
              <tr key={catalog.catalog_id}>
                <td>
                  <input
                    checked={selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet.has(catalog.catalog_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelection(catalog.catalog_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowDetailSection catalog={catalog} />
                <RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowActionSection catalog={catalog} />
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No governance policy catalogs saved yet.</p>
      )}
    </>
  );
}
