// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorMetadataFormSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorMetadataFormSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorPatchTextareaSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorPatchTextareaSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Hierarchy step editor</strong>
        <p>Edit one captured step directly. Empty JSON clears the current patch.</p>
      </div>
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
        <RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorMetadataFormSection model={model} />
      ) : (
        <p className="empty-state">Select a hierarchy step row and choose Edit to stage it in the editor.</p>
      )}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
        <RuntimeProviderProvenanceGovernanceCatalogHierarchyEditorPatchTextareaSection model={model} />
      ) : null}
    </div>
  );
}
