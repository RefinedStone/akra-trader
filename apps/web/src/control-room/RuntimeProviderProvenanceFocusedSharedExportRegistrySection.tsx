// @ts-nocheck
export function RuntimeProviderProvenanceFocusedSharedExportRegistrySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Team-shared export registry</strong>
        <p>
          {sharedProviderProvenanceExports.length
            ? `${sharedProviderProvenanceExports.length} shared export snapshot(s) are available for this focus.`
            : "No shared provider provenance exports recorded for this focus yet."}
        </p>
      </div>
      {sharedProviderProvenanceExportsLoading ? (
        <p className="empty-state">Loading shared export registry…</p>
      ) : null}
      {sharedProviderProvenanceExportsError ? (
        <p className="market-data-workflow-feedback">
          Shared registry load failed: {sharedProviderProvenanceExportsError}
        </p>
      ) : null}
      {sharedProviderProvenanceExports.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Exported</th>
              <th>Focus</th>
              <th>Filter</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sharedProviderProvenanceExports.map((entry) => (
              <tr key={entry.job_id}>
                <td>{formatTimestamp(entry.exported_at ?? entry.created_at)}</td>
                <td>
                  <strong>{entry.focus_label ?? "Unknown focus"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.market_data_provider ?? "n/a"} / {entry.venue ?? "n/a"} / {entry.symbol ?? "n/a"} · {entry.timeframe ?? "n/a"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.result_count} result(s) from {entry.provider_provenance_count} provenance incident(s)
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Requested by {entry.requested_by_tab_label ?? entry.requested_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <strong>{entry.filter_summary ?? "No filter summary recorded."}</strong>
                  <p className="run-lineage-symbol-copy">
                    Providers: {entry.provider_labels.length ? entry.provider_labels.join(", ") : "n/a"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Vendor fields: {entry.vendor_fields.length ? entry.vendor_fields.join(", ") : "n/a"}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void copySharedProviderProvenanceExport(entry);
                      }}
                      type="button"
                    >
                      Copy export
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void loadSharedProviderProvenanceExportHistory(entry.job_id);
                      }}
                      type="button"
                    >
                      {selectedSharedProviderProvenanceExportJobId === entry.job_id
                        && selectedSharedProviderProvenanceExportHistory
                        ? "Hide history"
                        : "View history"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </>
  );
}
