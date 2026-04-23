// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryHistoryTableSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryHistoryTableSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryRevisionHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeRegistryId ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Registry revision history</strong>
        <p>Review saved board revisions, apply them to the workbench, or restore them as the active shared scheduler board.</p>
      </div>
      {providerProvenanceSchedulerNarrativeRegistryHistoryLoading ? (
        <p className="empty-state">Loading registry revisions…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeRegistryHistoryError ? (
        <p className="market-data-workflow-feedback">
          Registry revision history failed: {providerProvenanceSchedulerNarrativeRegistryHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeRegistryHistory ? (
        <RuntimeProviderProvenanceSchedulerNarrativeRegistryHistoryTableSection model={model} />
      ) : null}
    </div>
  ) : null;
}
