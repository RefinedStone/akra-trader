// @ts-nocheck
export function RuntimeProviderProvenanceAnalyticsRecentExportsSection({ model }: { model: any }) {
  const {} = model;

  if (!providerProvenanceDashboardLayout.show_recent_exports) {
    return null;
  }

  return (
    <div>
      <h3>Cross-focus results</h3>
      {providerProvenanceAnalytics.recent_exports.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Exported</th>
              <th>Focus</th>
              <th>Providers</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceAnalytics.recent_exports.map((entry) => (
              <tr key={`cross-focus-${entry.job_id}`}>
                <td>{formatTimestamp(entry.exported_at ?? entry.created_at)}</td>
                <td>
                  <strong>{entry.focus_label ?? "Unknown focus"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.market_data_provider ?? "n/a"} / {entry.symbol ?? "n/a"} ·{" "}
                    {entry.timeframe ?? "n/a"}
                  </p>
                </td>
                <td>
                  <strong>{entry.provider_labels.join(", ") || "n/a"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.vendor_fields.join(", ") || "n/a"}
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
                        void focusMarketInstrumentFromProviderExport(entry);
                      }}
                      type="button"
                    >
                      Focus triage
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void loadSharedProviderProvenanceExportHistory(entry.job_id);
                      }}
                      type="button"
                    >
                      View history
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">
          No shared provider provenance exports match the current analytics query.
        </p>
      )}
    </div>
  );
}
