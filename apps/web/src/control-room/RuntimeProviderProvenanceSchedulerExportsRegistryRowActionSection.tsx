// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportsRegistryRowActionSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            void copySharedProviderProvenanceSchedulerExport(entry);
          }}
          type="button"
        >
          Copy export
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void loadProviderProvenanceSchedulerExportHistory(entry.job_id);
          }}
          type="button"
        >
          View history
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void escalateSharedProviderProvenanceSchedulerExport(entry);
          }}
          disabled={entry.approval_required && entry.approval_state !== "approved"}
          type="button"
        >
          Escalate
        </button>
      </div>
    </td>
  );
}
