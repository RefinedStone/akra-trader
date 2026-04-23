// @ts-nocheck
export function RuntimeProviderProvenanceFocusedPersistedExportHistorySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Persisted export history</strong>
        <p>
          {marketDataProvenanceExportHistory.length
            ? `${marketDataProvenanceExportHistory.length} saved export snapshot(s) are available in this browser.`
            : "No persisted provider provenance exports recorded yet."}
        </p>
      </div>
      {marketDataProvenanceExportHistory.length ? (
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
            {marketDataProvenanceExportHistory.slice(0, 8).map((entry) => (
              <tr key={entry.export_id}>
                <td>{formatTimestamp(entry.exported_at)}</td>
                <td>
                  <strong>{entry.focus_label}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.provider} / {entry.venue} / {entry.symbol} · {entry.timeframe}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.result_count} result(s) from {entry.provider_provenance_count} provenance incident(s)
                  </p>
                </td>
                <td>
                  <strong>{formatMarketDataProvenanceExportFilterSummary(entry.filter)}</strong>
                  <p className="run-lineage-symbol-copy">
                    Providers: {entry.provider_labels.length ? entry.provider_labels.join(", ") : "n/a"}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void copySavedMarketDataProvenanceExport(entry);
                      }}
                      type="button"
                    >
                      Copy export
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => restoreMarketDataProvenanceExportFilter(entry)}
                      type="button"
                    >
                      Load filters
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
