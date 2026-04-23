// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogVersionsTableSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogVersionsTableSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogVersionsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Catalog revision history</strong>
        <p>Stage a previous linked-template snapshot or restore it as the active policy catalog.</p>
      </div>
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryLoading ? (
        <p className="empty-state">Loading policy catalog revisions…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError ? (
        <p className="market-data-workflow-feedback">
          Policy catalog revision history failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory ? (
        <RuntimeProviderProvenanceGovernancePolicyCatalogVersionsTableSection model={model} />
      ) : (
        <p className="empty-state">Select a policy catalog row and open Versions to inspect revisions.</p>
      )}
    </div>
  );
}
