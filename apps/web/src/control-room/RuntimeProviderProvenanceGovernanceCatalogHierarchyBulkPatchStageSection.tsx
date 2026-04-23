// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkLayoutPatchStageSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkLayoutPatchStageSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkQueryPatchStageSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkQueryPatchStageSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkPatchStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="filter-bar">
      <RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkQueryPatchStageSection model={model} />
      <RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkLayoutPatchStageSection model={model} />
    </div>
  );
}
