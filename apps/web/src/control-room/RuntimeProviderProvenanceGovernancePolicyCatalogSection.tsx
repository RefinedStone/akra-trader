// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkEditSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkEditSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogRegistryTableSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogRegistryTableSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogVersionsSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogVersionsSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Governance policy catalogs</strong>
          <p>Reuse named policy bundles, review catalog revisions, and bulk-govern shared queue defaults without editing each catalog one by one.</p>
        </div>
        <RuntimeProviderProvenanceGovernancePolicyCatalogBulkEditSection model={model} />
        <RuntimeProviderProvenanceGovernancePolicyCatalogRegistryTableSection model={model} />
        <RuntimeProviderProvenanceGovernancePolicyCatalogVersionsSection model={model} />
      </div>
    </>
  );
}
