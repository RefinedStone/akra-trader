// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogRowSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogRowSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Catalog</th>
          <th>Defaults</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.map((catalog) => (
          <tr key={`provider-scheduler-stitched-governance-registry-catalog-${catalog.catalog_id}`}>
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogRowSection
              catalog={catalog}
              model={model}
            />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
