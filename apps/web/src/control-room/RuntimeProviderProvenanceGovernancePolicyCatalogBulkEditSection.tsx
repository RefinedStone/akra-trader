// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkActionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkActionSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkMetadataStageSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkMetadataStageSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkEditSection({ model }: { model: any }) {
  const {} = model;

  return providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length ? (
    <div className="filter-bar">
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkMetadataStageSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkActionSection model={model} />
    </div>
  ) : null;
}
