// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionStateSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionStateSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSummarySection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSummarySection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Selection</span>
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionStateSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkSelectionSummarySection model={model} />
    </label>
  );
}
