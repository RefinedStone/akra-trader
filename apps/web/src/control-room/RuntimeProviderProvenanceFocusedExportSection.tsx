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
      <h3>Provider provenance export (증거 내보내기)</h3>
      <div className="run-filter-workbench market-data-provenance-workbench">
        <div className="run-filter-workbench-head">
          <div className="market-data-provenance-copy">
            <strong>필터된 Provider readback incident</strong>
            <p>
              현재 focus의 Lineage, Ingestion, Provider readback evidence를 drill pack으로 묶습니다.
              필터는 이 브라우저에 유지되고, 복사한 export는 shared registry에도 기록됩니다.
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
              Drill pack 복사
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
