// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <label>
      <span>Action</span>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          disabled={
            !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
            || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
          }
          onClick={() => {
            void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("update");
          }}
          type="button"
        >
          {providerProvenanceSchedulerStitchedReportViewBulkAction === "update"
            ? "Previewing…"
            : "Preview bulk edit"}
        </button>
      </div>
    </label>
  );
}
