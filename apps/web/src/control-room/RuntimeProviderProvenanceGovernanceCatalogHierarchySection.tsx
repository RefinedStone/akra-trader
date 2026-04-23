// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkPatchStageSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkPatchStageSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStageSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStageSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyTableSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyTableSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Catalog hierarchy steps</strong>
          <p>Edit reusable hierarchy steps, bulk-govern selected steps, and restore an older step snapshot without restoring the whole catalog.</p>
        </div>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog ? (
          <>
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkSelectionStageSection model={model} />
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyBulkPatchStageSection model={model} />
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyTableSection model={model} />
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorSection model={model} />
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsSection model={model} />
          </>
        ) : (
          <p className="empty-state">Select a policy catalog row and open Versions to inspect hierarchy steps.</p>
        )}
      </div>
    </>
  );
}
