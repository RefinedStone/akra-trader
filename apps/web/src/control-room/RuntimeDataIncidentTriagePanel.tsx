// @ts-nocheck
import { RuntimeProviderProvenanceFocusedExportSection } from "./RuntimeProviderProvenanceFocusedExportSection";
import { RuntimeProviderProvenanceFocusedIngestionJobsSection } from "./RuntimeProviderProvenanceFocusedIngestionJobsSection";
import { RuntimeProviderProvenanceFocusedLineageHistorySection } from "./RuntimeProviderProvenanceFocusedLineageHistorySection";
export function RuntimeDataIncidentTriagePanel({ model }: { model: any }) {
  const {} = model;

  return (
              <PanelDisclosure
                defaultOpen={true}
                summary={
                  activeMarketInstrument && focusedMarketWorkflowSummary
                    ? `${focusedMarketWorkflowSummary.lineageCount} lineage snapshots · ${focusedMarketWorkflowSummary.ingestionJobCount} ingestion jobs · ${focusedMarketWorkflowSummary.linkedAlertCount} linked alerts for ${focusedMarketWorkflowSummary.focusLabel}.`
                    : "Select a market-data instrument to inspect lineage and ingestion workflow history."
                }
                title="Data incident triage"
              >
                {marketStatus ? (
                  <>
                    <div className="market-data-workflow-toolbar">
                      <div className="market-data-workflow-focus-copy">
                        <strong>
                          {focusedMarketWorkflowSummary?.focusLabel ?? "No triage focus selected"}
                        </strong>
                        <p>
                          {marketDataWorkflowLoading
                            ? "Refreshing lineage and ingestion workflow history..."
                            : marketDataWorkflowError
                              ? `History load failed: ${marketDataWorkflowError}`
                              : focusedMarketWorkflowSummary?.latestLineage
                                ? `Latest lineage snapshot recorded ${formatTimestamp(focusedMarketWorkflowSummary.latestLineage.recorded_at)} with ${formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage.validation_claim)} claim. ${focusedMarketWorkflowSummary.linkedAlertCount} active alert(s) and ${focusedMarketWorkflowSummary.linkedIncidentCount} incident event(s) are linked to this focus.`
                                : autoLinkedMarketInstrumentLink
                                  ? `Runtime alerts currently resolve to ${autoLinkedMarketInstrumentLink.symbol} · ${autoLinkedMarketInstrumentLink.timeframe}, but no lineage history has been recorded yet.`
                                  : "No lineage or ingestion history recorded for the current focus."}
                        </p>
                        {focusedMultiSymbolPrimaryLink ? (
                          <p className="market-data-workflow-policy-copy">
                            Multi-symbol primary focus: {focusedMultiSymbolPrimaryLink.primaryFocusReason} Candidate order: {focusedMultiSymbolPrimaryLink.candidateLabels.join(", ")}.
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
                            Copy filtered export
                          </button>
                          <span className="market-data-workflow-export-copy">
                            {focusedMarketProviderProvenanceCount
                              ? `${filteredFocusedMarketProviderProvenanceEvents.length} filtered result(s) from ${focusedMarketProviderProvenanceCount} linked provider-provenance incident(s).`
                              : "No linked incident currently exposes provider market-context provenance."}
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
                            <span>Failed jobs</span>
                            <strong>{focusedMarketWorkflowSummary.failedJobCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Latest claim</span>
                            <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage?.validation_claim)}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Latest job</span>
                            <strong>
                              {focusedMarketWorkflowSummary.latestJob
                                ? `${formatWorkflowToken(focusedMarketWorkflowSummary.latestJob.status)} / ${formatWorkflowToken(focusedMarketWorkflowSummary.latestJob.operation)}`
                                : "n/a"}
                            </strong>
                          </div>
                          <div className="metric-tile">
                            <span>Linked alerts</span>
                            <strong>{focusedMarketWorkflowSummary.linkedAlertCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Incident history</span>
                            <strong>{focusedMarketWorkflowSummary.incidentHistoryCount}</strong>
                          </div>
                          <div className="metric-tile">
                            <span>Provenance incidents</span>
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
                        <div>
                          <h3>Lineage incident history</h3>
                          {focusedMarketIncidentHistory.length ? (
                            <table className="data-table">
                              <thead>
                                <tr>
                                  <th>When</th>
                                  <th>Source</th>
                                  <th>Signal</th>
                                  <th>Detail</th>
                                </tr>
                              </thead>
                              <tbody>
                                {focusedMarketIncidentHistory.map((entry) => (
                                  <tr key={entry.entryId}>
                                    <td>{formatTimestamp(entry.occurredAt)}</td>
                                    <td>
                                      <span className={`market-data-incident-badge is-${entry.tone}`.trim()}>
                                        {entry.sourceLabel}
                                      </span>
                                    </td>
                                    <td>{entry.statusLabel}</td>
                                    <td>
                                      <strong>{entry.summary}</strong>
                                      <p className="run-lineage-symbol-copy">{entry.detail}</p>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          ) : (
                            <p className="empty-state">No alert-linked lineage incident history recorded for this focus.</p>
                          )}
                        </div>
                        <RuntimeProviderProvenanceFocusedExportSection model={model} />
                      </>
                    ) : (
                      <p className="empty-state">No market-data instrument is currently selected for triage.</p>
                    )}
                  </>
                ) : (
                  <p className="empty-state">Load market-data status before reviewing lineage workflow history.</p>
                )}
              </PanelDisclosure>
  );
}
