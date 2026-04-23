// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionActionSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionActionSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStateSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStateSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="filter-bar">
      <RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStateSection model={model} />
      <RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionActionSection model={model} />
    </div>
  );
}
