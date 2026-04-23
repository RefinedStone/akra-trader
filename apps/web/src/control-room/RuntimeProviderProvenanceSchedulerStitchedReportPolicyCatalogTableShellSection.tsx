// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogRowDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogRowDetailSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogTableShellSection({
  model,
  SelectionSection,
}: {
  model: any;
  SelectionSection: any;
}) {
  const {} = model;

  return providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th>Catalog</th>
          <th>Defaults</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((catalog) => (
          <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogRowDetailSection
            SelectionSection={SelectionSection}
            catalog={catalog}
            key={`provider-scheduler-stitched-governance-catalog-${catalog.catalog_id}`}
            model={model}
          />
        ))}
      </tbody>
    </table>
  ) : (
    <p className="empty-state">No stitched report policy catalogs match the current search.</p>
  );
}
