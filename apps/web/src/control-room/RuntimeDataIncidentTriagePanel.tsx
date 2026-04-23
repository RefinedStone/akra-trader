// @ts-nocheck
import { RuntimeProviderProvenanceFocusedExportSection } from "./RuntimeProviderProvenanceFocusedExportSection";
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
                          <div>
                            <h3>Lineage history</h3>
                            {marketDataLineageHistory.length ? (
                              <table className="data-table">
                                <thead>
                                  <tr>
                                    <th>Recorded</th>
                                    <th>Sync</th>
                                    <th>Claim</th>
                                    <th>Boundary</th>
                                    <th>Signal</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {marketDataLineageHistory.slice(0, 6).map((record) => (
                                    <tr key={record.history_id}>
                                      <td>{formatTimestamp(record.recorded_at)}</td>
                                      <td>{record.sync_status}</td>
                                      <td>{formatWorkflowToken(record.validation_claim)}</td>
                                      <td title={record.boundary_id ?? undefined}>
                                        {record.boundary_id ? shortenIdentifier(record.boundary_id, 22) : "n/a"}
                                      </td>
                                      <td>
                                        <strong>
                                          {record.failure_count_24h} failures / 24h
                                          {record.gap_window_count ? ` · ${record.gap_window_count} gaps` : ""}
                                        </strong>
                                        <p className="run-lineage-symbol-copy">
                                          {record.issues.length ? record.issues.join(", ") : "No lineage issues recorded."}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          Window: {formatRange(record.first_timestamp, record.last_timestamp)}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          Checkpoint: {record.checkpoint_id ? shortenIdentifier(record.checkpoint_id, 22) : "n/a"}
                                        </p>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            ) : (
                              <p className="empty-state">No lineage history recorded for this focus.</p>
                            )}
                          </div>
                          <div>
                            <h3>Ingestion jobs</h3>
                            {marketDataIngestionJobs.length ? (
                              <table className="data-table">
                                <thead>
                                  <tr>
                                    <th>Finished</th>
                                    <th>Status</th>
                                    <th>Operation</th>
                                    <th>Fetched</th>
                                    <th>Detail</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {marketDataIngestionJobs.slice(0, 6).map((job) => (
                                    <tr key={job.job_id}>
                                      <td>{formatTimestamp(job.finished_at)}</td>
                                      <td>{job.status}</td>
                                      <td>{job.operation}</td>
                                      <td>{job.fetched_candle_count}</td>
                                      <td>
                                        <strong>{job.duration_ms} ms</strong>
                                        <p className="run-lineage-symbol-copy">
                                          Claim: {formatWorkflowToken(job.validation_claim)}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          Requested: {formatRange(job.requested_start_at, job.requested_end_at)}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          {job.last_error ? truncateLabel(job.last_error, 84) : "No job error recorded."}
                                        </p>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            ) : (
                              <p className="empty-state">No ingestion jobs recorded for this focus.</p>
                            )}
                          </div>
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
