// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkSelectionSection({ model }: { model: any }) {
  const {} = model;

  return providerProvenanceSchedulerStitchedReportViews.length ? (
    <div className="provider-provenance-governance-bar">
      <div className="provider-provenance-governance-summary">
        <strong>{selectedProviderProvenanceSchedulerStitchedReportViewIds.length} selected</strong>
        <span>
          {
            selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter(
              (entry) => entry.status === "active",
            ).length
          }{" "}
          active ·{" "}
          {
            selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter(
              (entry) => entry.status === "deleted",
            ).length
          }{" "}
          deleted
        </span>
      </div>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
          type="button"
        >
          {selectedProviderProvenanceSchedulerStitchedReportViewIds.length
            === providerProvenanceSchedulerStitchedReportViews.length
            ? "Clear all"
            : "Select all"}
        </button>
        <button
          className="ghost-button"
          disabled={
            !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
            || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
          }
          onClick={() => {
            void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("delete");
          }}
          type="button"
        >
          {providerProvenanceSchedulerStitchedReportViewBulkAction === "delete"
            ? "Previewing…"
            : "Preview delete"}
        </button>
        <button
          className="ghost-button"
          disabled={
            !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
            || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
          }
          onClick={() => {
            void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("restore");
          }}
          type="button"
        >
          {providerProvenanceSchedulerStitchedReportViewBulkAction === "restore"
            ? "Previewing…"
            : "Preview restore"}
        </button>
      </div>
    </div>
  ) : null;
}
