// @ts-nocheck
export function RuntimeProviderProvenanceFocusedSharedExportRegistrySection({ model }: { model: any }) {
  const {
    sharedProviderProvenanceExports,
    sharedProviderProvenanceExportsLoading,
    sharedProviderProvenanceExportsError,
    formatTimestamp,
    copySharedProviderProvenanceExport,
    loadSharedProviderProvenanceExportHistory,
    selectedSharedProviderProvenanceExportJobId,
    selectedSharedProviderProvenanceExportHistory,
  } = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>팀 공유 export registry</strong>
        <p>
          {sharedProviderProvenanceExports.length
            ? `이 focus에 공유된 export snapshot ${sharedProviderProvenanceExports.length}건이 있습니다.`
            : "이 focus에 공유된 Provider provenance export가 아직 없습니다."}
        </p>
      </div>
      {sharedProviderProvenanceExportsLoading ? (
        <p className="empty-state">Shared export registry를 불러오는 중입니다.</p>
      ) : null}
      {sharedProviderProvenanceExportsError ? (
        <p className="market-data-workflow-feedback">
          Shared registry 로드 실패: {sharedProviderProvenanceExportsError}
        </p>
      ) : null}
      {sharedProviderProvenanceExports.length ? (
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
            {sharedProviderProvenanceExports.map((entry) => (
              <tr key={entry.job_id}>
                <td>{formatTimestamp(entry.exported_at ?? entry.created_at)}</td>
                <td>
                  <strong>{entry.focus_label ?? "알 수 없는 focus"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.market_data_provider ?? "n/a"} / {entry.venue ?? "n/a"} / {entry.symbol ?? "n/a"} · {entry.timeframe ?? "n/a"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Provenance incident {entry.provider_provenance_count}건 중 결과 {entry.result_count}건
                  </p>
                  <p className="run-lineage-symbol-copy">
                    요청 탭: {entry.requested_by_tab_label ?? entry.requested_by_tab_id ?? "알 수 없음"}
                  </p>
                </td>
                <td>
                  <strong>{entry.filter_summary ?? "기록된 filter summary가 없습니다."}</strong>
                  <p className="run-lineage-symbol-copy">
                    Providers: {entry.provider_labels.length ? entry.provider_labels.join(", ") : "없음"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Vendor fields: {entry.vendor_fields.length ? entry.vendor_fields.join(", ") : "없음"}
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
                      Export 복사
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
                        ? "이력 숨기기"
                        : "이력 보기"}
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
