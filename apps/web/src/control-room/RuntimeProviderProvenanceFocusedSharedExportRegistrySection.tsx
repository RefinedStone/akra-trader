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
        <strong>팀 공유 내보내기 이력</strong>
        <p>
          {sharedProviderProvenanceExports.length
            ? `이 대상에 공유된 내보내기 이력 ${sharedProviderProvenanceExports.length}건이 있습니다.`
            : "이 대상에 공유된 제공처 근거 내보내기 이력이 아직 없습니다."}
        </p>
      </div>
      {sharedProviderProvenanceExportsLoading ? (
        <p className="empty-state">팀 공유 내보내기 이력을 불러오는 중입니다.</p>
      ) : null}
      {sharedProviderProvenanceExportsError ? (
        <p className="market-data-workflow-feedback">
          팀 공유 이력 로드 실패: {sharedProviderProvenanceExportsError}
        </p>
      ) : null}
      {sharedProviderProvenanceExports.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>내보낸 시각</th>
              <th>대상</th>
              <th>필터</th>
              <th>동작</th>
            </tr>
          </thead>
          <tbody>
            {sharedProviderProvenanceExports.map((entry) => (
              <tr key={entry.job_id}>
                <td>{formatTimestamp(entry.exported_at ?? entry.created_at)}</td>
                <td>
                  <strong>{entry.focus_label ?? "알 수 없는 대상"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.market_data_provider ?? "n/a"} / {entry.venue ?? "n/a"} / {entry.symbol ?? "n/a"} · {entry.timeframe ?? "n/a"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    제공처 문제 {entry.provider_provenance_count}건 중 결과 {entry.result_count}건
                  </p>
                  <p className="run-lineage-symbol-copy">
                    요청 탭: {entry.requested_by_tab_label ?? entry.requested_by_tab_id ?? "알 수 없음"}
                  </p>
                </td>
                <td>
                  <strong>{entry.filter_summary ?? "기록된 필터 요약이 없습니다."}</strong>
                  <p className="run-lineage-symbol-copy">
                    제공처: {entry.provider_labels.length ? entry.provider_labels.join(", ") : "없음"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    제공처 필드: {entry.vendor_fields.length ? entry.vendor_fields.join(", ") : "없음"}
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
                      내보내기 복사
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
