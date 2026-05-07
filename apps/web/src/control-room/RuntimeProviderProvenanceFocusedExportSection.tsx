// @ts-nocheck
import { RuntimeProviderProvenanceFocusedPersistedExportHistorySection } from "./RuntimeProviderProvenanceFocusedPersistedExportHistorySection";
import { RuntimeProviderProvenanceFocusedReadbackSection } from "./RuntimeProviderProvenanceFocusedReadbackSection";
import { RuntimeProviderProvenanceFocusedSharedExportRegistrySection } from "./RuntimeProviderProvenanceFocusedSharedExportRegistrySection";

export function RuntimeProviderProvenanceFocusedExportSection({ model }: { model: any }) {
  const {
    copyFocusedMarketWorkflowExport,
    resetMarketDataProvenanceExportFilter,
    marketDataProvenanceExportHistory,
    clearMarketDataProvenanceExportHistory,
  } = model;

  return (
    <div>
      <h3>수집 근거 내보내기</h3>
      <div className="run-filter-workbench market-data-provenance-workbench">
        <div className="run-filter-workbench-head">
          <div className="market-data-provenance-copy">
            <strong>필터된 제공처 문제</strong>
            <p>
              현재 점검 대상의 수집 이력, 수집 작업, 제공처 확인 근거를 하나로 묶습니다.
              필터는 이 브라우저에 유지되고, 복사한 자료는 팀 공유 이력에도 기록됩니다.
            </p>
          </div>
          <div className="run-filter-workbench-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void copyFocusedMarketWorkflowExport();
              }}
              type="button"
            >
              점검 자료 복사
            </button>
            <button
              className="ghost-button"
              onClick={resetMarketDataProvenanceExportFilter}
              type="button"
            >
              필터 초기화
            </button>
            {marketDataProvenanceExportHistory.length ? (
              <button
                className="ghost-button"
                onClick={clearMarketDataProvenanceExportHistory}
                type="button"
              >
                이력 지우기
              </button>
            ) : null}
          </div>
        </div>
        <RuntimeProviderProvenanceFocusedReadbackSection model={model} />
        <RuntimeProviderProvenanceFocusedPersistedExportHistorySection model={model} />
        <RuntimeProviderProvenanceFocusedSharedExportRegistrySection model={model} />
      </div>
    </div>
  );
}
