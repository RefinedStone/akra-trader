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
                    ? `${focusedMarketWorkflowSummary.focusLabel} 기준 Lineage ${focusedMarketWorkflowSummary.lineageCount}건, Ingestion job ${focusedMarketWorkflowSummary.ingestionJobCount}건, 연결 Alert ${focusedMarketWorkflowSummary.linkedAlertCount}건을 확인합니다.`
                    : "Market-data instrument를 선택하면 Lineage와 Ingestion workflow 이력을 확인할 수 있습니다."
                }
                title="Data incident triage (데이터 이슈 점검)"
              >
                {marketStatus ? (
                  <>
                    <div className="market-data-workflow-toolbar">
                      <div className="market-data-workflow-focus-copy">
                        <strong>
                          {focusedMarketWorkflowSummary?.focusLabel ?? "선택된 triage focus 없음"}
                        </strong>
                        <p>
                          {marketDataWorkflowLoading
                            ? "Lineage와 Ingestion workflow 이력을 새로 불러오는 중입니다."
                            : marketDataWorkflowError
                              ? `이력 로드 실패: ${marketDataWorkflowError}`
                              : focusedMarketWorkflowSummary?.latestLineage
                                ? `최근 Lineage snapshot은 ${formatTimestamp(focusedMarketWorkflowSummary.latestLineage.recorded_at)}에 기록됐고 claim은 ${formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage.validation_claim)}입니다. 이 focus에 활성 Alert ${focusedMarketWorkflowSummary.linkedAlertCount}건, Incident event ${focusedMarketWorkflowSummary.linkedIncidentCount}건이 연결되어 있습니다.`
                                : autoLinkedMarketInstrumentLink
                                  ? `Runtime alert는 현재 ${autoLinkedMarketInstrumentLink.symbol} · ${autoLinkedMarketInstrumentLink.timeframe}로 연결되지만, 아직 Lineage 이력은 없습니다.`
                                  : "현재 focus에 기록된 Lineage 또는 Ingestion 이력이 없습니다."}
                        </p>
                        {focusedMultiSymbolPrimaryLink ? (
                          <p className="market-data-workflow-policy-copy">
                            Multi-symbol primary focus: {focusedMultiSymbolPrimaryLink.primaryFocusReason} 후보 순서: {focusedMultiSymbolPrimaryLink.candidateLabels.join(", ")}.
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
                            Drill pack 복사
                          </button>
                          <span className="market-data-workflow-export-copy">
                            {focusedMarketProviderProvenanceCount
                              ? `필터된 Provider 결과 ${filteredFocusedMarketProviderProvenanceEvents.length}건과 Lineage evidence를 묶습니다.`
                              : "이 focus의 Lineage 및 Ingestion evidence를 묶습니다."}
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
                            <span>Focused sync</span>
                            <strong>{activeMarketInstrument.sync_status}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Lineage snapshots</span>
                            <strong>{focusedMarketWorkflowSummary.lineageCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Review snapshots</span>
                            <strong>{focusedMarketWorkflowSummary.reviewSnapshotCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>실패 Job</span>
                            <strong>{focusedMarketWorkflowSummary.failedJobCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>최근 Claim</span>
                            <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage?.validation_claim)}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>최근 Job</span>
                            <strong>
                              {focusedMarketWorkflowSummary.latestJob
                                ? `${formatWorkflowToken(focusedMarketWorkflowSummary.latestJob.status)} / ${formatWorkflowToken(focusedMarketWorkflowSummary.latestJob.operation)}`
                                : "n/a"}
                            </strong>
                          </div>
                          <div className="metric-tile">
                            <span>연결 Alert</span>
                            <strong>{focusedMarketWorkflowSummary.linkedAlertCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Incident 이력</span>
                            <strong>{focusedMarketWorkflowSummary.incidentHistoryCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Provenance incident</span>
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
                      <p className="empty-state">현재 triage할 market-data instrument가 선택되지 않았습니다.</p>
                    )}
                  </>
                ) : (
                  <p className="empty-state">Lineage workflow 이력을 보려면 먼저 market-data status를 불러와야 합니다.</p>
                )}
              </PanelDisclosure>
  );
}
