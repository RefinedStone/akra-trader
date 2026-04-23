// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsTableSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsTableSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Hierarchy step versions</strong>
        <p>Use the loaded catalog revision history to stage a prior step snapshot or restore that step only.</p>
      </div>
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.length ? (
        <RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsTableSection model={model} />
      ) : (
        <p className="empty-state">Select a hierarchy step and open Versions to inspect step snapshots across catalog revisions.</p>
      )}
    </div>
  );
}
