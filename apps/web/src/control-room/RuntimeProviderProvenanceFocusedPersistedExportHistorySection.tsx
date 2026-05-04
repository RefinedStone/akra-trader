// @ts-nocheck
export function RuntimeProviderProvenanceFocusedPersistedExportHistorySection({ model }: { model: any }) {
  const {
    marketDataProvenanceExportHistory,
    formatTimestamp,
    formatMarketDataProvenanceExportFilterSummary,
    copySavedMarketDataProvenanceExport,
    restoreMarketDataProvenanceExportFilter,
  } = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>저장된 export 이력</strong>
        <p>
          {marketDataProvenanceExportHistory.length
            ? `이 브라우저에 저장된 export snapshot ${marketDataProvenanceExportHistory.length}건이 있습니다.`
            : "아직 저장된 Provider provenance export가 없습니다."}
        </p>
      </div>
      {marketDataProvenanceExportHistory.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Export 시각</th>
              <th>Focus</th>
              <th>Filter</th>
              <th>동작</th>
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
                    Provenance incident {entry.provider_provenance_count}건 중 결과 {entry.result_count}건
                  </p>
                </td>
                <td>
                  <strong>{formatMarketDataProvenanceExportFilterSummary(entry.filter)}</strong>
                  <p className="run-lineage-symbol-copy">
                    Providers: {entry.provider_labels.length ? entry.provider_labels.join(", ") : "없음"}
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
                      Export 복사
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => restoreMarketDataProvenanceExportFilter(entry)}
                      type="button"
                    >
                      필터 불러오기
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
