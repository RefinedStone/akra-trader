// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsTableSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsTableSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Template versions</strong>
            <p>Stage a prior snapshot into the editor or restore a specific revision.</p>
          </div>
          {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryLoading ? (
            <p className="empty-state">Loading hierarchy step template revisions…</p>
          ) : null}
          {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryError ? (
            <p className="market-data-workflow-feedback">
              Hierarchy step template revision load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryError}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory ? (
            <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsTableSection model={model} />
          ) : (
            <p className="empty-state">Select a hierarchy step template row and open Versions to inspect revisions.</p>
          )}
        </div>
      ) : null}
    </>
  );
}
