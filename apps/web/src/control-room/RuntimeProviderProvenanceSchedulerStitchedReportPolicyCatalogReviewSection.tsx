// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogTableShellSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogTableShellSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogReviewSection({
  model,
  SelectionSection,
}: {
  model: any;
  SelectionSection: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Stitched report policy catalogs</strong>
        <p>
          Review only governance catalogs that can drive stitched report view approval
          defaults, then apply those defaults or jump into the shared catalog workspace.
        </p>
      </div>
      <div className="provider-provenance-governance-summary">
        <strong>
          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length} stitched catalog(s)
        </strong>
        <span>
          {
            providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter(
              (entry) => entry.status === "active",
            ).length
          }{" "}
          active ·{" "}
          {
            providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter(
              (entry) => entry.status === "deleted",
            ).length
          }{" "}
          deleted
        </span>
      </div>
      <div className="filter-bar">
        <label>
          <span>Search</span>
          <input
            onChange={(event) => {
              setProviderProvenanceSchedulerStitchedReportGovernanceCatalogSearch(
                event.target.value,
              );
            }}
            placeholder="catalog, guidance, policy"
            type="text"
            value={providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch}
          />
        </label>
      </div>
      <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogTableShellSection
        SelectionSection={SelectionSection}
        model={model}
      />
    </div>
  );
}
