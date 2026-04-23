// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueBatchActionsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-governance-editor">
      <div className="market-data-provenance-history-head">
        <strong>Batch queue actions</strong>
        <p>Approve or apply multiple governance plans at once after filtering the queue to the exact lane, priority, or policy template slice you want.</p>
      </div>
      <div className="provider-provenance-governance-summary">
        <strong>
          Selected {selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} of {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} filtered plan(s)
        </strong>
        <span>
          {selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.map((plan) => shortenIdentifier(plan.plan_id, 8)).join(", ") || "No plans selected"}
        </span>
      </div>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections}
          type="button"
        >
          {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length > 0
            && selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length === filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length
            ? "Clear filtered"
            : "Select filtered"}
        </button>
        <button
          className="ghost-button"
          disabled={!selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length || providerProvenanceSchedulerNarrativeGovernanceBatchAction !== null}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeGovernancePlanBatch("approve");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernanceBatchAction === "approve"
            ? "Approving…"
            : "Approve selected"}
        </button>
        <button
          className="ghost-button"
          disabled={!selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length || providerProvenanceSchedulerNarrativeGovernanceBatchAction !== null}
          onClick={() => {
            void runProviderProvenanceSchedulerNarrativeGovernancePlanBatch("apply");
          }}
          type="button"
        >
          {providerProvenanceSchedulerNarrativeGovernanceBatchAction === "apply"
            ? "Applying…"
            : "Apply selected"}
        </button>
      </div>
    </div>
  );
}
