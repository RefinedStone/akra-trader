// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyTemplateVersionsTableSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateVersionsTableSection";

export function RuntimeProviderProvenanceGovernancePolicyTemplateVersionsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Policy template revision history</strong>
        <p>Review policy snapshots, stage an older revision into the editor, or restore it as the active template.</p>
      </div>
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryLoading ? (
        <p className="empty-state">Loading policy template revisions…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryError ? (
        <p className="market-data-workflow-feedback">
          Policy template revision history failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory ? (
        <RuntimeProviderProvenanceGovernancePolicyTemplateVersionsTableSection model={model} />
      ) : (
        <p className="empty-state">Select a policy template row and open Versions to inspect revisions.</p>
      )}
    </div>
  );
}
