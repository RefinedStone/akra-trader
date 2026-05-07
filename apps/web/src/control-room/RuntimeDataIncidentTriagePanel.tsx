// @ts-nocheck
import { RuntimeProviderProvenanceFocusedExportSection } from "./RuntimeProviderProvenanceFocusedExportSection";
import { RuntimeProviderProvenanceFocusedIngestionJobsSection } from "./RuntimeProviderProvenanceFocusedIngestionJobsSection";
import { RuntimeProviderProvenanceFocusedLineageIncidentHistorySection } from "./RuntimeProviderProvenanceFocusedLineageIncidentHistorySection";
import { RuntimeProviderProvenanceFocusedLineageHistorySection } from "./RuntimeProviderProvenanceFocusedLineageHistorySection";
export function RuntimeDataIncidentTriagePanel({ model }: { model: any }) {
  const {
    PanelDisclosure,
    activeMarketInstrument,
    focusedMarketWorkflowSummary,
    marketStatus,
    marketDataWorkflowLoading,
    marketDataWorkflowError,
    formatTimestamp,
    formatWorkflowToken,
    autoLinkedMarketInstrumentLink,
    focusedMultiSymbolPrimaryLink,
    incidentFocusedInstruments,
    buildMarketDataInstrumentFocusKey,
    activeMarketInstrumentKey,
    handleMarketInstrumentFocus,
    resolveMarketDataSymbol,
    copyFocusedMarketWorkflowExport,
    focusedMarketProviderProvenanceCount,
    filteredFocusedMarketProviderProvenanceEvents,
    marketDataWorkflowExportFeedback,
  } = model;

  return (
              <PanelDisclosure
                defaultOpen={true}
                summary={
                  activeMarketInstrument && focusedMarketWorkflowSummary
                    ? `${focusedMarketWorkflowSummary.focusLabel} 기준 수집 이력 ${focusedMarketWorkflowSummary.lineageCount}건, 수집 작업 ${focusedMarketWorkflowSummary.ingestionJobCount}건, 연결 알림 ${focusedMarketWorkflowSummary.linkedAlertCount}건을 확인합니다.`
                    : "시장 데이터 종목을 선택하면 수집 이력과 작업 기록을 확인할 수 있습니다."
                }
                title="데이터 문제 점검"
              >
                {marketStatus ? (
                  <>
                    <div className="market-data-workflow-toolbar">
                      <div className="market-data-workflow-focus-copy">
                        <strong>
                          {focusedMarketWorkflowSummary?.focusLabel ?? "선택된 점검 대상 없음"}
                        </strong>
                        <p>
                          {marketDataWorkflowLoading
                            ? "수집 이력과 작업 기록을 새로 불러오는 중입니다."
                            : marketDataWorkflowError
                              ? `이력 로드 실패: ${marketDataWorkflowError}`
                              : focusedMarketWorkflowSummary?.latestLineage
                                ? `최근 수집 이력은 ${formatTimestamp(focusedMarketWorkflowSummary.latestLineage.recorded_at)}에 기록됐고 검증 상태는 ${formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage.validation_claim)}입니다. 이 대상에는 활성 알림 ${focusedMarketWorkflowSummary.linkedAlertCount}건, 문제 이력 ${focusedMarketWorkflowSummary.linkedIncidentCount}건이 연결되어 있습니다.`
                                : autoLinkedMarketInstrumentLink
                                  ? `운용 알림은 현재 ${autoLinkedMarketInstrumentLink.symbol} · ${autoLinkedMarketInstrumentLink.timeframe}에 연결되어 있지만 아직 수집 이력은 없습니다.`
                                  : "현재 대상에 기록된 수집 이력이나 작업 기록이 없습니다."}
                        </p>
                        {focusedMultiSymbolPrimaryLink ? (
                          <p className="market-data-workflow-policy-copy">
                            여러 종목 중 우선 확인 대상: {focusedMultiSymbolPrimaryLink.primaryFocusReason}. 후보 순서: {focusedMultiSymbolPrimaryLink.candidateLabels.join(", ")}.
                          </p>
                        ) : null}
                      </div>
                      {incidentFocusedInstruments.length ? (
                        <div className="market-data-workflow-chip-row">
                          {incidentFocusedInstruments.map((instrument) => {
                            const focusKey = buildMarketDataInstrumentFocusKey(instrument);
                            const active = focusKey === activeMarketInstrumentKey;
                            return (
                              <button
                                className={`ghost-button ${active ? "is-active" : ""}`.trim()}
                                key={focusKey}
                                onClick={() => {
                                  void handleMarketInstrumentFocus(instrument);
                                }}
                                type="button"
                              >
                                {resolveMarketDataSymbol(instrument.instrument_id)} · {instrument.timeframe}
                              </button>
                            );
                          })}
                        </div>
                      ) : null}
                      {activeMarketInstrument && focusedMarketWorkflowSummary ? (
                        <div className="market-data-workflow-action-row">
                          <button
                            className="ghost-button"
                            onClick={() => {
                              void copyFocusedMarketWorkflowExport();
                            }}
                            type="button"
                          >
                            점검 자료 복사
                          </button>
                          <span className="market-data-workflow-export-copy">
                            {focusedMarketProviderProvenanceCount
                              ? `필터된 제공처 결과 ${filteredFocusedMarketProviderProvenanceEvents.length}건과 수집 근거를 묶습니다.`
                              : "이 대상의 수집 이력과 작업 근거를 묶습니다."}
                          </span>
                        </div>
                      ) : null}
                      {marketDataWorkflowExportFeedback ? (
                        <p className="market-data-workflow-feedback">
                          {marketDataWorkflowExportFeedback}
                        </p>
                      ) : null}
                    </div>
                    {activeMarketInstrument && focusedMarketWorkflowSummary ? (
                      <>
                        <div className="status-grid">
                          <div className="metric-tile">
                            <span>수집 상태</span>
                            <strong>{activeMarketInstrument.sync_status}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>수집 이력</span>
                            <strong>{focusedMarketWorkflowSummary.lineageCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>검토 이력</span>
                            <strong>{focusedMarketWorkflowSummary.reviewSnapshotCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>실패한 작업</span>
                            <strong>{focusedMarketWorkflowSummary.failedJobCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>최근 검증</span>
                            <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage?.validation_claim)}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>최근 작업</span>
                            <strong>
                              {focusedMarketWorkflowSummary.latestJob
                                ? `${formatWorkflowToken(focusedMarketWorkflowSummary.latestJob.status)} / ${formatWorkflowToken(focusedMarketWorkflowSummary.latestJob.operation)}`
                                : "n/a"}
                            </strong>
                          </div>
                          <div className="metric-tile">
                            <span>연결 알림</span>
                            <strong>{focusedMarketWorkflowSummary.linkedAlertCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>문제 이력</span>
                            <strong>{focusedMarketWorkflowSummary.incidentHistoryCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>제공처 문제</span>
                            <strong>
                              {filteredFocusedMarketProviderProvenanceEvents.length}
                              {` / ${focusedMarketProviderProvenanceCount}`}
                            </strong>
                          </div>
                        </div>
                        <div className="status-grid-two-column">
                          <RuntimeProviderProvenanceFocusedLineageHistorySection model={model} />
                          <RuntimeProviderProvenanceFocusedIngestionJobsSection model={model} />
                        </div>
                        <RuntimeProviderProvenanceFocusedLineageIncidentHistorySection model={model} />
                        <RuntimeProviderProvenanceFocusedExportSection model={model} />
                      </>
                    ) : (
                      <p className="empty-state">현재 점검할 시장 데이터 종목이 선택되지 않았습니다.</p>
                    )}
                  </>
                ) : (
                  <p className="empty-state">수집 이력을 보려면 먼저 시장 데이터 상태를 불러와야 합니다.</p>
                )}
              </PanelDisclosure>
  );
}
