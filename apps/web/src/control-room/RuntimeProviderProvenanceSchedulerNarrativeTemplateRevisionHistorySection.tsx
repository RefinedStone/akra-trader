// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateHistoryTableSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateHistoryTableSection";

export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRevisionHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeTemplateId ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Template revision history</strong>
        <p>Inspect immutable snapshots, apply them to the workbench, or restore them as the active template.</p>
      </div>
      {providerProvenanceSchedulerNarrativeTemplateHistoryLoading ? (
        <p className="empty-state">Loading template revisions…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplateHistoryError ? (
        <p className="market-data-workflow-feedback">
          Template revision history failed: {providerProvenanceSchedulerNarrativeTemplateHistoryError}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeTemplateHistory ? (
        <RuntimeProviderProvenanceSchedulerNarrativeTemplateHistoryTableSection model={model} />
      ) : null}
    </div>
  ) : null;
}
