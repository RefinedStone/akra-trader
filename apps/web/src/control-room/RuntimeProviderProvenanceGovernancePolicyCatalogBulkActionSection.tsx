// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkDeleteActionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkDeleteActionSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkRestoreActionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkRestoreActionSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkUpdateActionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkUpdateActionSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Action</span>
      <div className="market-data-provenance-history-actions">
        <RuntimeProviderProvenanceGovernancePolicyCatalogBulkDeleteActionSection model={model} />
        <RuntimeProviderProvenanceGovernancePolicyCatalogBulkRestoreActionSection model={model} />
        <RuntimeProviderProvenanceGovernancePolicyCatalogBulkUpdateActionSection model={model} />
      </div>
    </label>
  );
}
