// @ts-nocheck
import { RuntimeProviderProvenanceWorkspaceCards } from "./RuntimeProviderProvenanceWorkspaceCards";
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
                        <div>
                          <h3>Provider provenance export</h3>
                          <div className="run-filter-workbench market-data-provenance-workbench">
                            <div className="run-filter-workbench-head">
                              <div className="market-data-provenance-copy">
                                <strong>Filtered provider readback incidents</strong>
                                <p>
                                  Export the incidents whose selected market context came back from a provider-native
                                  field path. Filters stay local to this browser, while copied exports also land in
                                  the shared registry.
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
                                  Copy filtered export
                                </button>
                                <button
                                  className="ghost-button"
                                  onClick={resetMarketDataProvenanceExportFilter}
                                  type="button"
                                >
                                  Reset filters
                                </button>
                                {marketDataProvenanceExportHistory.length ? (
                                  <button
                                    className="ghost-button"
                                    onClick={clearMarketDataProvenanceExportHistory}
                                    type="button"
                                  >
                                    Clear history
                                  </button>
                                ) : null}
                              </div>
                            </div>
                            <div className="filter-bar">
                              <label>
                                <span>Provider</span>
                                <select
                                  onChange={(event) =>
                                    setMarketDataProvenanceExportFilter((current) => ({
                                      ...current,
                                      provider: event.target.value,
                                    }))
                                  }
                                  value={marketDataProvenanceExportFilter.provider}
                                >
                                  <option value={ALL_FILTER_VALUE}>All providers</option>
                                  {marketDataProvenanceExportProviderOptions.map((provider) => (
                                    <option key={provider} value={provider}>
                                      {provider}
                                    </option>
                                  ))}
                                </select>
                              </label>
                              <label>
                                <span>Vendor field</span>
                                <select
                                  onChange={(event) =>
                                    setMarketDataProvenanceExportFilter((current) => ({
                                      ...current,
                                      vendor_field: event.target.value,
                                    }))
                                  }
                                  value={marketDataProvenanceExportFilter.vendor_field}
                                >
                                  <option value={ALL_FILTER_VALUE}>All vendor fields</option>
                                  {marketDataProvenanceExportVendorFieldOptions.map((vendorField) => (
                                    <option key={vendorField} value={vendorField}>
                                      {vendorField}
                                    </option>
                                  ))}
                                </select>
                              </label>
                              <label>
                                <span>Sort</span>
                                <select
                                  onChange={(event) =>
                                    setMarketDataProvenanceExportFilter((current) => ({
                                      ...current,
                                      sort: normalizeMarketDataProvenanceExportSort(event.target.value),
                                    }))
                                  }
                                  value={marketDataProvenanceExportFilter.sort}
                                >
                                  <option value="newest">Newest first</option>
                                  <option value="oldest">Oldest first</option>
                                  <option value="provider">Provider</option>
                                  <option value="severity">Severity</option>
                                </select>
                              </label>
                              <label>
                                <span>Search</span>
                                <input
                                  onChange={(event) =>
                                    setMarketDataProvenanceExportFilter((current) => ({
                                      ...current,
                                      search_query: event.target.value,
                                    }))
                                  }
                                  placeholder="summary, provider, path"
                                  type="search"
                                  value={marketDataProvenanceExportFilter.search_query}
                                />
                              </label>
                            </div>
                            <div className="run-filter-summary-chip-row">
                              <span className="run-filter-summary-chip">
                                {filteredFocusedMarketProviderProvenanceEvents.length} filtered result(s)
                              </span>
                              <span className="run-filter-summary-chip">
                                {focusedMarketProviderProvenanceCount} total provenance incident(s)
                              </span>
                              <span className="run-filter-summary-chip">
                                {formatMarketDataProvenanceExportFilterSummary(marketDataProvenanceExportFilter)}
                              </span>
                            </div>
                            {filteredFocusedMarketProviderProvenanceEvents.length ? (
                              <table className="data-table">
                                <thead>
                                  <tr>
                                    <th>When</th>
                                    <th>Provider</th>
                                    <th>Signal</th>
                                    <th>Provenance</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {filteredFocusedMarketProviderProvenanceEvents.slice(0, 8).map((record) => (
                                    <tr key={`provider-provenance-${record.event.event_id}`}>
                                      <td>{formatTimestamp(record.event.timestamp)}</td>
                                      <td>
                                        <strong>{record.provider}</strong>
                                        <p className="run-lineage-symbol-copy">
                                          Vendor field: {record.vendorField}
                                        </p>
                                      </td>
                                      <td>
                                        <strong>{record.event.summary}</strong>
                                        <p className="run-lineage-symbol-copy">
                                          {formatWorkflowToken(record.event.kind)} / {formatWorkflowToken(record.event.severity)}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          {record.event.external_reference
                                            ? `External ref: ${record.event.external_reference}`
                                            : "No external reference recorded."}
                                        </p>
                                      </td>
                                      <td>
                                        <strong>{record.provenanceSummary}</strong>
                                        {record.fieldSummaries.map((fieldSummary) => (
                                          <p className="run-lineage-symbol-copy" key={fieldSummary}>
                                            {fieldSummary}
                                          </p>
                                        ))}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            ) : (
                              <p className="empty-state">
                                No provider provenance incidents match the current export filters.
                              </p>
                            )}
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
                            <div className="market-data-provenance-history-head">
                              <strong>Team-shared export registry</strong>
                              <p>
                                {sharedProviderProvenanceExports.length
                                  ? `${sharedProviderProvenanceExports.length} shared export snapshot(s) are available for this focus.`
                                  : "No shared provider provenance exports recorded for this focus yet."}
                              </p>
                            </div>
                            {sharedProviderProvenanceExportsLoading ? (
                              <p className="empty-state">Loading shared export registry…</p>
                            ) : null}
                            {sharedProviderProvenanceExportsError ? (
                              <p className="market-data-workflow-feedback">
                                Shared registry load failed: {sharedProviderProvenanceExportsError}
                              </p>
                            ) : null}
                            {sharedProviderProvenanceExports.length ? (
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
                                  {sharedProviderProvenanceExports.map((entry) => (
                                    <tr key={entry.job_id}>
                                      <td>{formatTimestamp(entry.exported_at ?? entry.created_at)}</td>
                                      <td>
                                        <strong>{entry.focus_label ?? "Unknown focus"}</strong>
                                        <p className="run-lineage-symbol-copy">
                                          {entry.market_data_provider ?? "n/a"} / {entry.venue ?? "n/a"} / {entry.symbol ?? "n/a"} · {entry.timeframe ?? "n/a"}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          {entry.result_count} result(s) from {entry.provider_provenance_count} provenance incident(s)
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          Requested by {entry.requested_by_tab_label ?? entry.requested_by_tab_id ?? "unknown tab"}
                                        </p>
                                      </td>
                                      <td>
                                        <strong>{entry.filter_summary ?? "No filter summary recorded."}</strong>
                                        <p className="run-lineage-symbol-copy">
                                          Providers: {entry.provider_labels.length ? entry.provider_labels.join(", ") : "n/a"}
                                        </p>
                                        <p className="run-lineage-symbol-copy">
                                          Vendor fields: {entry.vendor_fields.length ? entry.vendor_fields.join(", ") : "n/a"}
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
                                            Copy export
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
                                              ? "Hide history"
                                              : "View history"}
                                          </button>
                                        </div>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            ) : null}
                            <div className="market-data-provenance-shared-history">
                              <div className="market-data-provenance-history-head">
                                <strong>Analytics and cross-focus query</strong>
                                <p>
                                  Query the shared provider provenance registry across focuses and roll the results up
                                  into provider, vendor-field, and focus hotspots.
                                </p>
                              </div>
                              <div className="filter-bar">
                                <label>
                                  <span>Scope</span>
                                  <select
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        scope: event.target.value === "all_focuses" ? "all_focuses" : "current_focus",
                                      }))
                                    }
                                    value={providerProvenanceAnalyticsQuery.scope}
                                  >
                                    <option value="current_focus">Current focus</option>
                                    <option value="all_focuses">All focuses</option>
                                  </select>
                                </label>
                                <label>
                                  <span>Window</span>
                                  <select
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        window_days: [7, 14, 30].includes(Number(event.target.value))
                                          ? Number(event.target.value)
                                          : 14,
                                      }))
                                    }
                                    value={providerProvenanceAnalyticsQuery.window_days}
                                  >
                                    <option value={7}>7 days</option>
                                    <option value={14}>14 days</option>
                                    <option value={30}>30 days</option>
                                  </select>
                                </label>
                                <label>
                                  <span>Provider</span>
                                  <select
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        provider_label: event.target.value,
                                      }))
                                    }
                                    value={providerProvenanceAnalyticsQuery.provider_label}
                                  >
                                    <option value={ALL_FILTER_VALUE}>All providers</option>
                                    {(providerProvenanceAnalytics?.available_filters.provider_labels ?? []).map((provider) => (
                                      <option key={provider} value={provider}>
                                        {provider}
                                      </option>
                                    ))}
                                  </select>
                                </label>
                                <label>
                                  <span>Vendor field</span>
                                  <select
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        vendor_field: event.target.value,
                                      }))
                                    }
                                    value={providerProvenanceAnalyticsQuery.vendor_field}
                                  >
                                    <option value={ALL_FILTER_VALUE}>All vendor fields</option>
                                    {(providerProvenanceAnalytics?.available_filters.vendor_fields ?? []).map((fieldName) => (
                                      <option key={fieldName} value={fieldName}>
                                        {fieldName}
                                      </option>
                                    ))}
                                  </select>
                                </label>
                                <label>
                                  <span>Market data</span>
                                  <select
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        market_data_provider: event.target.value,
                                      }))
                                    }
                                    value={providerProvenanceAnalyticsQuery.market_data_provider}
                                  >
                                    <option value={ALL_FILTER_VALUE}>All market-data providers</option>
                                    {(providerProvenanceAnalytics?.available_filters.market_data_providers ?? []).map((provider) => (
                                      <option key={provider} value={provider}>
                                        {provider}
                                      </option>
                                    ))}
                                  </select>
                                </label>
                                <label>
                                  <span>Requester</span>
                                  <select
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        requested_by_tab_id: event.target.value,
                                      }))
                                    }
                                    value={providerProvenanceAnalyticsQuery.requested_by_tab_id}
                                  >
                                    <option value={ALL_FILTER_VALUE}>All requesters</option>
                                    {(providerProvenanceAnalytics?.available_filters.requested_by_tab_ids ?? []).map((requester) => (
                                      <option key={requester} value={requester}>
                                        {requester}
                                      </option>
                                    ))}
                                  </select>
                                </label>
                                <label>
                                  <span>Search</span>
                                  <input
                                    onChange={(event) =>
                                      setProviderProvenanceAnalyticsQuery((current) => ({
                                        ...current,
                                        search_query: event.target.value,
                                      }))
                                    }
                                    placeholder="focus, requester, provider"
                                    type="search"
                                    value={providerProvenanceAnalyticsQuery.search_query}
                                  />
                                </label>
                              </div>
                              <div className="run-filter-summary-chip-row">
                                <span className="run-filter-summary-chip">
                                  {formatProviderProvenanceAnalyticsQuerySummary(providerProvenanceAnalyticsQuery)}
                                </span>
                                <span className="run-filter-summary-chip">
                                  {providerProvenanceAnalytics
                                    ? `${providerProvenanceAnalytics.totals.export_count} matched export(s)`
                                    : "Analytics pending"}
                                </span>
                                <span className="run-filter-summary-chip">
                                  {providerProvenanceAnalytics
                                    ? `${providerProvenanceAnalytics.totals.unique_focus_count} focus anchor(s)`
                                    : "Waiting for rollups"}
                                </span>
                                <span className="run-filter-summary-chip">
                                  Layout {providerProvenanceDashboardLayout.highlight_panel}
                                </span>
                              </div>
                              <div className="provider-provenance-workspace-grid">
                                <RuntimeProviderProvenanceWorkspaceCards model={model} />
                                <div className="provider-provenance-workspace-card">
                                  <div className="market-data-provenance-history-head">
                                    <strong>Scheduled provenance reports</strong>
                                    <p>Persist the current analytics view as a durable report and run it on demand or when due.</p>
                                  </div>
                                  <div className="filter-bar">
                                    <label>
                                      <span>Name</span>
                                      <input
                                        onChange={(event) =>
                                          setProviderProvenanceReportDraft((current) => ({
                                            ...current,
                                            name: event.target.value,
                                          }))
                                        }
                                        placeholder="BTC weekly provenance report"
                                        type="text"
                                        value={providerProvenanceReportDraft.name}
                                      />
                                    </label>
                                    <label>
                                      <span>Description</span>
                                      <input
                                        onChange={(event) =>
                                          setProviderProvenanceReportDraft((current) => ({
                                            ...current,
                                            description: event.target.value,
                                          }))
                                        }
                                        placeholder="weekly drift roll-up"
                                        type="text"
                                        value={providerProvenanceReportDraft.description}
                                      />
                                    </label>
                                    <label>
                                      <span>Cadence</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceReportDraft((current) => ({
                                            ...current,
                                            cadence: event.target.value === "weekly" ? "weekly" : "daily",
                                          }))
                                        }
                                        value={providerProvenanceReportDraft.cadence}
                                      >
                                        <option value="daily">Daily</option>
                                        <option value="weekly">Weekly</option>
                                      </select>
                                    </label>
                                    <label>
                                      <span>Status</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceReportDraft((current) => ({
                                            ...current,
                                            status: event.target.value === "paused" ? "paused" : "scheduled",
                                          }))
                                        }
                                        value={providerProvenanceReportDraft.status}
                                      >
                                        <option value="scheduled">Scheduled</option>
                                        <option value="paused">Paused</option>
                                      </select>
                                    </label>
                                    <label>
                                      <span>Preset</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceReportDraft((current) => ({
                                            ...current,
                                            preset_id: event.target.value,
                                          }))
                                        }
                                        value={providerProvenanceReportDraft.preset_id}
                                      >
                                        <option value="">No preset link</option>
                                        {providerProvenanceAnalyticsPresets.map((entry) => (
                                          <option key={entry.preset_id} value={entry.preset_id}>
                                            {entry.name}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label>
                                      <span>View</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceReportDraft((current) => ({
                                            ...current,
                                            view_id: event.target.value,
                                          }))
                                        }
                                        value={providerProvenanceReportDraft.view_id}
                                      >
                                        <option value="">No view link</option>
                                        {providerProvenanceDashboardViews.map((entry) => (
                                          <option key={entry.view_id} value={entry.view_id}>
                                            {entry.name}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                  </div>
                                  <div className="run-filter-workbench-actions">
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        void createCurrentProviderProvenanceScheduledReport();
                                      }}
                                      type="button"
                                    >
                                      Save report
                                    </button>
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        void runDueSharedProviderProvenanceScheduledReports();
                                      }}
                                      type="button"
                                    >
                                      Run due now
                                    </button>
                                  </div>
                                  {providerProvenanceScheduledReportsLoading ? (
                                    <p className="empty-state">Loading scheduled reports…</p>
                                  ) : null}
                                  {providerProvenanceScheduledReportsError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduled report registry load failed: {providerProvenanceScheduledReportsError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceScheduledReports.length ? (
                                    <table className="data-table">
                                      <thead>
                                        <tr>
                                          <th>Report</th>
                                          <th>Schedule</th>
                                          <th>Action</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {providerProvenanceScheduledReports.slice(0, 6).map((entry) => (
                                          <tr key={entry.report_id}>
                                            <td>
                                              <strong>{entry.name}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.filter_summary}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.view_id ? `View ${shortenIdentifier(entry.view_id, 10)}` : "No view link"}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{entry.status} · {entry.cadence}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                Next {formatTimestamp(entry.next_run_at)}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                Last {formatTimestamp(entry.last_run_at)}
                                              </p>
                                            </td>
                                            <td>
                                              <div className="market-data-provenance-history-actions">
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void runSharedProviderProvenanceScheduledReport(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Run now
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void applyProviderProvenanceWorkspaceQuery(entry, {
                                                      includeLayout: true,
                                                      feedbackLabel: `Report ${entry.name}`,
                                                    });
                                                  }}
                                                  type="button"
                                                >
                                                  Apply
                                                </button>
                                                {entry.last_export_job_id ? (
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void copyProviderProvenanceExportJobById(entry.last_export_job_id!, entry.name);
                                                    }}
                                                    type="button"
                                                  >
                                                    Copy latest export
                                                  </button>
                                                ) : null}
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void toggleProviderProvenanceScheduledReportHistory(entry.report_id);
                                                  }}
                                                  type="button"
                                                >
                                                  {selectedProviderProvenanceScheduledReportId === entry.report_id
                                                    && selectedProviderProvenanceScheduledReportHistory
                                                    ? "Hide history"
                                                    : "View history"}
                                                </button>
                                              </div>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  ) : (
                                    <p className="empty-state">No scheduled provenance reports saved yet.</p>
                                  )}
                                  {selectedProviderProvenanceScheduledReportId ? (
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Scheduled report audit trail</strong>
                                        <p>
                                          Review report runs and copy any generated analytics export artifact.
                                        </p>
                                      </div>
                                      {providerProvenanceScheduledReportHistoryLoading ? (
                                        <p className="empty-state">Loading scheduled report history…</p>
                                      ) : null}
                                      {providerProvenanceScheduledReportHistoryError ? (
                                        <p className="market-data-workflow-feedback">
                                          Scheduled report history failed: {providerProvenanceScheduledReportHistoryError}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceScheduledReportHistory ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>When</th>
                                              <th>Action</th>
                                              <th>Detail</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {selectedProviderProvenanceScheduledReportHistory.history.map((entry) => (
                                              <tr key={entry.audit_id}>
                                                <td>{formatTimestamp(entry.recorded_at)}</td>
                                                <td>
                                                  <strong>{entry.action}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.source_tab_label ?? entry.source_tab_id ?? "unknown source"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{entry.detail}</strong>
                                                  {entry.export_job_id ? (
                                                    <div className="market-data-provenance-history-actions">
                                                      <button
                                                        className="ghost-button"
                                                        onClick={() => {
                                                          void copyProviderProvenanceExportJobById(
                                                            entry.export_job_id!,
                                                            selectedProviderProvenanceScheduledReportHistory.report.name,
                                                          );
                                                        }}
                                                        type="button"
                                                      >
                                                        Copy export
                                                      </button>
                                                    </div>
                                                  ) : null}
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : null}
                                    </div>
                                  ) : null}
                                </div>
                              </div>
                              {providerProvenanceSchedulerAnalyticsLoading && !providerProvenanceSchedulerAnalytics ? (
                                <p className="empty-state">Loading scheduler automation trends…</p>
                              ) : null}
                              {providerProvenanceSchedulerAnalyticsError ? (
                                <p className="market-data-workflow-feedback">
                                  Scheduler automation analytics failed: {providerProvenanceSchedulerAnalyticsError}
                                </p>
                              ) : null}
                              {providerProvenanceSchedulerHistoryError ? (
                                <p className="market-data-workflow-feedback">
                                  Scheduler automation history failed: {providerProvenanceSchedulerHistoryError}
                                </p>
                              ) : null}
                              {providerProvenanceSchedulerCurrent ? (
                                <div
                                  className={`market-data-provenance-shared-history ${
                                    providerProvenanceDashboardLayout.highlight_panel === "scheduler_alerts"
                                      ? "is-highlighted"
                                      : ""
                                  }`.trim()}
                                  ref={providerProvenanceSchedulerAutomationRef}
                                >
                                  <div className="market-data-provenance-history-head">
                                    <strong>Scheduler automation</strong>
                                    <p>
                                      Persisted health history and daily trend buckets for provenance report
                                      automation.
                                    </p>
                                  </div>
                                  <div className="market-data-provenance-history-actions">
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        void copyProviderProvenanceSchedulerHealthJsonExport();
                                      }}
                                      type="button"
                                    >
                                      Copy JSON export
                                    </button>
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        void shareProviderProvenanceSchedulerHealthExport();
                                      }}
                                      type="button"
                                    >
                                      Share export
                                    </button>
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        void downloadProviderProvenanceSchedulerHealthCsv();
                                      }}
                                      type="button"
                                    >
                                      Download CSV page
                                    </button>
                                    {providerProvenanceSchedulerDrilldownBucketKey ? (
                                      <button
                                        className="ghost-button"
                                        onClick={() => {
                                          setProviderProvenanceSchedulerDrilldownBucketKey(null);
                                        }}
                                        type="button"
                                      >
                                        Reset drill-down
                                      </button>
                                    ) : null}
                                  </div>
                                  <div className="status-grid">
                                    <div className="metric-tile">
                                      <span>Current status</span>
                                      <strong>{formatWorkflowToken(providerProvenanceSchedulerCurrent.status)}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Due backlog</span>
                                      <strong>{providerProvenanceSchedulerCurrent.due_report_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Peak lag</span>
                                      <strong>{formatSchedulerLagSeconds(providerProvenanceSchedulerCurrent.max_due_lag_seconds)}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Total executed</span>
                                      <strong>{providerProvenanceSchedulerCurrent.total_executed_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Success / failure</span>
                                      <strong>
                                        {providerProvenanceSchedulerCurrent.success_count} / {providerProvenanceSchedulerCurrent.failure_count}
                                      </strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Last success</span>
                                      <strong>{formatTimestamp(providerProvenanceSchedulerCurrent.last_success_at)}</strong>
                                    </div>
                                  </div>
                                  <p className="market-data-workflow-export-copy">
                                    {providerProvenanceSchedulerCurrent.summary}
                                  </p>
                                  <div className="run-filter-summary-chip-row">
                                    <span className="run-filter-summary-chip">
                                      Interval {providerProvenanceSchedulerCurrent.interval_seconds}s · batch {providerProvenanceSchedulerCurrent.batch_limit}
                                    </span>
                                    <span className="run-filter-summary-chip">
                                      Last cycle {formatTimestamp(providerProvenanceSchedulerCurrent.last_cycle_finished_at)}
                                    </span>
                                    {providerProvenanceSchedulerCurrent.oldest_due_at ? (
                                      <span className="run-filter-summary-chip">
                                        Oldest due {formatTimestamp(providerProvenanceSchedulerCurrent.oldest_due_at)}
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerCurrent.last_error ? (
                                      <span className="run-filter-summary-chip">
                                        Last error {providerProvenanceSchedulerCurrent.last_error}
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerCurrent.issues.map((issue) => (
                                      <span className="run-filter-summary-chip" key={`provider-scheduler-issue-${issue}`}>
                                        {issue}
                                      </span>
                                    ))}
                                  </div>
                                  {providerProvenanceSchedulerAnalytics ? (
                                    <div className="status-grid-two-column market-data-provenance-time-series-grid">
                                      <div className="market-data-provenance-time-series-panel">
                                        <div className="market-data-provenance-history-head">
                                          <strong>Health status by day</strong>
                                          <p>
                                            Daily scheduler-cycle mix across the current provenance automation window.
                                          </p>
                                        </div>
                                        <div className="run-filter-summary-chip-row">
                                          <span className="run-filter-summary-chip">
                                            Peak cycle day {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.peak_cycle_bucket_label ?? "n/a"} · {" "}
                                            {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.peak_cycle_count} cycle(s)
                                          </span>
                                          <span className="run-filter-summary-chip">
                                            Latest {providerProvenanceSchedulerAnalytics.time_series.health_status.summary.latest_bucket_label ?? "n/a"} · {" "}
                                            {formatWorkflowToken(providerProvenanceSchedulerAnalytics.time_series.health_status.summary.latest_status)}
                                          </span>
                                        </div>
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Day</th>
                                              <th>Cycles</th>
                                              <th>Status mix</th>
                                              <th>Action</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceSchedulerAnalytics.time_series.health_status.series.map((bucket) => (
                                              <tr key={`provider-scheduler-health-${bucket.bucket_key}`}>
                                                <td>
                                                  <strong>{bucket.bucket_label}</strong>
                                                  <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                                                </td>
                                                <td>
                                                  <strong>{bucket.cycle_count} cycle(s)</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Executed {bucket.executed_report_count} report(s)
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(bucket.dominant_status)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Healthy {bucket.healthy_count} · lagging {bucket.lagging_count} · failed {bucket.failed_count}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">{bucket.latest_summary || "No scheduler events recorded."}</p>
                                                </td>
                                                <td>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      setProviderProvenanceSchedulerDrilldownBucketKey(bucket.bucket_key);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerDrilldownBucketKey === bucket.bucket_key
                                                      ? "Selected"
                                                      : "Hour view"}
                                                  </button>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      </div>
                                      <div className="market-data-provenance-time-series-panel">
                                        <div className="market-data-provenance-history-head">
                                          <strong>Lag and backlog trend</strong>
                                          <p>
                                            Daily peak lag, due backlog, and failure pressure for scheduler cycles.
                                          </p>
                                        </div>
                                        <div className="run-filter-summary-chip-row">
                                          <span className="run-filter-summary-chip">
                                            Peak lag {providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.peak_lag_bucket_label ?? "n/a"} · {" "}
                                            {formatSchedulerLagSeconds(providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.peak_lag_seconds)}
                                          </span>
                                          <span className="run-filter-summary-chip">
                                            Latest lag {formatSchedulerLagSeconds(providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.latest_lag_seconds)} · {" "}
                                            {providerProvenanceSchedulerAnalytics.time_series.lag_trend.summary.latest_due_report_count} due
                                          </span>
                                        </div>
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Day</th>
                                              <th>Lag</th>
                                              <th>Backlog</th>
                                              <th>Action</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceSchedulerAnalytics.time_series.lag_trend.series.map((bucket) => (
                                              <tr key={`provider-scheduler-lag-${bucket.bucket_key}`}>
                                                <td>
                                                  <strong>{bucket.bucket_label}</strong>
                                                  <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                                                </td>
                                                <td>
                                                  <strong>{formatSchedulerLagSeconds(bucket.peak_lag_seconds)}</strong>
                                                  <div className="market-data-provenance-timeseries-track">
                                                    <div
                                                      className="market-data-provenance-timeseries-bar is-warning"
                                                      style={{
                                                        width: resolveProviderProvenanceSeriesBarWidth(
                                                          bucket.peak_lag_seconds,
                                                          providerProvenanceSchedulerLagBarMax,
                                                        ),
                                                      }}
                                                    />
                                                  </div>
                                                  <p className="run-lineage-symbol-copy">
                                                    Latest {formatSchedulerLagSeconds(bucket.latest_lag_seconds)} · avg {formatSchedulerLagSeconds(bucket.average_lag_seconds)}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{bucket.peak_due_report_count} due report(s)</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Failures {bucket.failure_count} · executed {bucket.executed_report_count}
                                                  </p>
                                                </td>
                                                <td>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      setProviderProvenanceSchedulerDrilldownBucketKey(
                                                        bucket.bucket_key.slice(0, 10),
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerDrilldownBucketKey === bucket.bucket_key.slice(0, 10)
                                                      ? "Selected"
                                                      : "Hour view"}
                                                  </button>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      </div>
                                    </div>
                                  ) : null}
                                  {providerProvenanceSchedulerDrillDown ? (
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Hourly drill-down · {providerProvenanceSchedulerDrillDown.bucket_label}</strong>
                                        <p>
                                          Review hour-level scheduler pressure and the raw cycle records for the
                                          selected day bucket.
                                        </p>
                                      </div>
                                      <div className="run-filter-summary-chip-row">
                                        <span className="run-filter-summary-chip">
                                          {providerProvenanceSchedulerDrillDown.total_record_count} recorded cycle(s)
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Peak lag {formatSchedulerLagSeconds(providerProvenanceSchedulerDrillDown.lag_trend.summary.peak_lag_seconds)}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Latest {formatWorkflowToken(providerProvenanceSchedulerDrillDown.health_status.summary.latest_status)}
                                        </span>
                                      </div>
                                      <div className="status-grid-two-column market-data-provenance-time-series-grid">
                                        <div className="market-data-provenance-time-series-panel">
                                          <div className="market-data-provenance-history-head">
                                            <strong>Status by hour</strong>
                                            <p>Hour-level cycle mix for the selected day bucket.</p>
                                          </div>
                                          <table className="data-table">
                                            <thead>
                                              <tr>
                                                <th>Hour</th>
                                                <th>Cycles</th>
                                                <th>Status mix</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {providerProvenanceSchedulerDrillDown.health_status.series.map((bucket) => (
                                                <tr key={`provider-scheduler-hour-health-${bucket.bucket_key}`}>
                                                  <td>
                                                    <strong>{bucket.bucket_label}</strong>
                                                    <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                                                  </td>
                                                  <td>
                                                    <strong>{bucket.cycle_count} cycle(s)</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      Executed {bucket.executed_report_count} report(s)
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <strong>{formatWorkflowToken(bucket.latest_status)}</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      Healthy {bucket.healthy_count} · lagging {bucket.lagging_count} · failed {bucket.failed_count}
                                                    </p>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        </div>
                                        <div className="market-data-provenance-time-series-panel">
                                          <div className="market-data-provenance-history-head">
                                            <strong>Lag by hour</strong>
                                            <p>Peak and latest lag inside the selected scheduler day bucket.</p>
                                          </div>
                                          <table className="data-table">
                                            <thead>
                                              <tr>
                                                <th>Hour</th>
                                                <th>Lag</th>
                                                <th>Backlog</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {providerProvenanceSchedulerDrillDown.lag_trend.series.map((bucket) => (
                                                <tr key={`provider-scheduler-hour-lag-${bucket.bucket_key}`}>
                                                  <td>
                                                    <strong>{bucket.bucket_label}</strong>
                                                    <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                                                  </td>
                                                  <td>
                                                    <strong>{formatSchedulerLagSeconds(bucket.peak_lag_seconds)}</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      Latest {formatSchedulerLagSeconds(bucket.latest_lag_seconds)} · avg {formatSchedulerLagSeconds(bucket.average_lag_seconds)}
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <strong>{bucket.peak_due_report_count} due</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      Failures {bucket.failure_count}
                                                    </p>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        </div>
                                      </div>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Selected-day cycle records</strong>
                                        <p>
                                          The most recent recorded scheduler cycles inside the selected day bucket.
                                        </p>
                                      </div>
                                      {providerProvenanceSchedulerDrillDown.history.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Recorded</th>
                                              <th>Status</th>
                                              <th>Detail</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceSchedulerDrillDown.history.map((entry) => (
                                              <tr key={`provider-scheduler-drill-history-${entry.record_id}`}>
                                                <td>
                                                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.source_tab_label ?? entry.source_tab_id ?? "scheduler"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.status)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Lag {formatSchedulerLagSeconds(entry.max_due_lag_seconds)} · due {entry.due_report_count}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{entry.summary}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Executed {entry.last_executed_count} report(s) · cycle {entry.cycle_count}
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No hourly scheduler records were captured for the selected day.</p>
                                      )}
                                    </div>
                                  ) : null}
                                  <div className="market-data-provenance-history-head">
                                    <strong>Recent scheduler cycles</strong>
                                    <p>
                                      Review the persisted automation history that backs the trend surfaces.
                                    </p>
                                  </div>
                                  <div className="market-data-provenance-history-actions">
                                    <button
                                      className="ghost-button"
                                      disabled={!providerProvenanceSchedulerHistory?.previous_offset && providerProvenanceSchedulerHistoryOffset === 0}
                                      onClick={() => {
                                        setProviderProvenanceSchedulerHistoryOffset(
                                          providerProvenanceSchedulerHistory?.previous_offset ?? 0,
                                        );
                                      }}
                                      type="button"
                                    >
                                      Previous page
                                    </button>
                                    <button
                                      className="ghost-button"
                                      disabled={!(providerProvenanceSchedulerHistory?.has_more ?? false)}
                                      onClick={() => {
                                        if (typeof providerProvenanceSchedulerHistory?.next_offset === "number") {
                                          setProviderProvenanceSchedulerHistoryOffset(
                                            providerProvenanceSchedulerHistory.next_offset,
                                          );
                                        }
                                      }}
                                      type="button"
                                    >
                                      Next page
                                    </button>
                                    <span className="run-lineage-symbol-copy">
                                      {providerProvenanceSchedulerHistory
                                        ? `${providerProvenanceSchedulerHistory.query.offset + 1}-${providerProvenanceSchedulerHistory.query.offset + providerProvenanceSchedulerHistory.returned} of ${providerProvenanceSchedulerHistory.total}`
                                        : "Page 1"}
                                    </span>
                                  </div>
                                  {providerProvenanceSchedulerHistoryLoading && !providerProvenanceSchedulerRecentHistory.length ? (
                                    <p className="empty-state">Loading scheduler cycle history…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerRecentHistory.length ? (
                                    <table className="data-table">
                                      <thead>
                                        <tr>
                                          <th>Recorded</th>
                                          <th>Status</th>
                                          <th>Detail</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {providerProvenanceSchedulerRecentHistory.map((entry) => (
                                          <tr key={entry.record_id}>
                                            <td>
                                              <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.source_tab_label ?? entry.source_tab_id ?? "scheduler"}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{formatWorkflowToken(entry.status)}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                Lag {formatSchedulerLagSeconds(entry.max_due_lag_seconds)} · due {entry.due_report_count}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{entry.summary}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                Executed {entry.last_executed_count} report(s) · cycle {entry.cycle_count}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.last_error ?? (entry.issues.join(" · ") || "No blocking issues recorded.")}
                                              </p>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  ) : (
                                    <p className="empty-state">No scheduler cycle history recorded yet.</p>
                                  )}
                                  <div className="market-data-provenance-history-head">
                                    <strong>Scheduler alert occurrence timeline</strong>
                                    <p>
                                      Review paginated lag/failure occurrences without mixing them into the broader
                                      operator alert history.
                                    </p>
                                  </div>
                                  <div className="run-filter-summary-chip-row">
                                    <span className="run-filter-summary-chip">
                                      Total {providerProvenanceSchedulerAlertHistory?.summary.total_occurrences ?? 0} occurrence(s)
                                    </span>
                                    <span className="run-filter-summary-chip">
                                      Active {providerProvenanceSchedulerAlertHistory?.summary.active_count ?? 0} · resolved {" "}
                                      {providerProvenanceSchedulerAlertHistory?.summary.resolved_count ?? 0}
                                    </span>
                                    {(providerProvenanceSchedulerAlertHistory?.summary.by_category ?? []).map((entry) => (
                                      <span
                                        className="run-filter-summary-chip"
                                        key={`provider-scheduler-alert-summary-${entry.category}`}
                                      >
                                        {formatWorkflowToken(entry.category)} {entry.total} total · {entry.resolved_count} resolved
                                      </span>
                                    ))}
                                    <span className="run-filter-summary-chip">
                                      Facet {formatProviderProvenanceSchedulerNarrativeFacet(
                                        providerProvenanceAnalyticsQuery.scheduler_alert_narrative_facet,
                                      )}
                                    </span>
                                    {providerProvenanceSchedulerAlertHistory?.search_summary ? (
                                      <span className="run-filter-summary-chip">
                                        Search ranked · {providerProvenanceSchedulerAlertHistory.search_summary.matched_occurrences} match(es) · top {providerProvenanceSchedulerAlertHistory.search_summary.top_score}
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerAlertHistory?.search_summary?.operator_count ? (
                                      <span className="run-filter-summary-chip">
                                        Field ops {providerProvenanceSchedulerAlertHistory.search_summary.operator_count} · boolean {providerProvenanceSchedulerAlertHistory.search_summary.boolean_operator_count} · semantic {providerProvenanceSchedulerAlertHistory.search_summary.semantic_concept_count}
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerAlertHistory?.search_summary ? (
                                      <span className="run-filter-summary-chip">
                                        Index {providerProvenanceSchedulerAlertHistory.search_summary.indexed_occurrence_count} occurrence(s) · {providerProvenanceSchedulerAlertHistory.search_summary.indexed_term_count} term(s)
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerAlertHistory?.search_summary?.relevance_model ? (
                                      <span className="run-filter-summary-chip">
                                        {providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "external_scheduler_search_service"
                                          ? "External search service"
                                          : providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "standalone_persistent_scheduler_search_store"
                                            ? "Standalone persistent index"
                                            : providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "embedded_scheduler_search_service"
                                              ? "Embedded search service"
                                              : providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "record_backed_scheduler_search_projection"
                                                ? "Persistent index"
                                                : "Ephemeral index"} · {providerProvenanceSchedulerAlertHistory.search_summary.relevance_model}
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerAlertHistory?.search_summary?.retrieval_cluster_count ? (
                                      <span className="run-filter-summary-chip">
                                        Clustered {providerProvenanceSchedulerAlertHistory.search_summary.retrieval_cluster_count} group(s)
                                        {providerProvenanceSchedulerAlertHistory.search_summary.top_cluster_label
                                          ? ` · top ${providerProvenanceSchedulerAlertHistory.search_summary.top_cluster_label}`
                                          : ""}
                                      </span>
                                    ) : null}
                                    {providerProvenanceSchedulerAlertHistory?.search_analytics ? (
                                      <span className="run-filter-summary-chip">
                                        Feedback {providerProvenanceSchedulerAlertHistory.search_analytics.feedback_count} · pending {providerProvenanceSchedulerAlertHistory.search_analytics.pending_feedback_count} · approved {providerProvenanceSchedulerAlertHistory.search_analytics.approved_feedback_count} · tuned {providerProvenanceSchedulerAlertHistory.search_analytics.tuned_feature_count}
                                      </span>
                                    ) : null}
                                  </div>
                                  <div className="market-data-provenance-history-actions">
                                    <label className="run-form-field">
                                      <span>Category</span>
                                      <select
                                        value={providerProvenanceAnalyticsQuery.scheduler_alert_category}
                                        onChange={(event) => {
                                          setProviderProvenanceAnalyticsQuery((current) => ({
                                            ...current,
                                            scheduler_alert_category: event.target.value,
                                          }));
                                          setProviderProvenanceSchedulerAlertHistoryOffset(0);
                                        }}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All categories</option>
                                        {providerProvenanceSchedulerAlertCategoryOptions.map((value) => (
                                          <option key={`provider-scheduler-alert-category-${value}`} value={value}>
                                            {formatWorkflowToken(value)}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Status</span>
                                      <select
                                        value={providerProvenanceAnalyticsQuery.scheduler_alert_status}
                                        onChange={(event) => {
                                          setProviderProvenanceAnalyticsQuery((current) => ({
                                            ...current,
                                            scheduler_alert_status: event.target.value,
                                          }));
                                          setProviderProvenanceSchedulerAlertHistoryOffset(0);
                                        }}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All statuses</option>
                                        {providerProvenanceSchedulerAlertStatusOptions.map((value) => (
                                          <option key={`provider-scheduler-alert-status-${value}`} value={value}>
                                            {formatWorkflowToken(value)}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Narrative facet</span>
                                      <select
                                        value={providerProvenanceAnalyticsQuery.scheduler_alert_narrative_facet}
                                        onChange={(event) => {
                                          setProviderProvenanceAnalyticsQuery((current) => ({
                                            ...current,
                                            scheduler_alert_narrative_facet:
                                              event.target.value === "resolved_narratives"
                                              || event.target.value === "post_resolution_recovery"
                                              || event.target.value === "recurring_occurrences"
                                                ? event.target.value
                                                : "all_occurrences",
                                          }));
                                          setProviderProvenanceSchedulerAlertHistoryOffset(0);
                                        }}
                                      >
                                        {providerProvenanceSchedulerAlertNarrativeFacetOptions.map((value) => (
                                          <option key={`provider-scheduler-alert-facet-${value}`} value={value}>
                                            {formatProviderProvenanceSchedulerNarrativeFacet(
                                              value as ProviderProvenanceSchedulerOccurrenceNarrativeFacet,
                                            )}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Search</span>
                                      <input
                                        onChange={(event) => {
                                          setProviderProvenanceAnalyticsQuery((current) => ({
                                            ...current,
                                            search_query: event.target.value,
                                          }));
                                          setProviderProvenanceSchedulerAlertHistoryOffset(0);
                                        }}
                                        placeholder='status:resolved AND (recovered OR healthy) AND NOT category:failure'
                                        type="search"
                                        value={providerProvenanceAnalyticsQuery.search_query}
                                      />
                                    </label>
                                    {providerProvenanceSchedulerAlertHistory?.search_summary?.query_plan.length ? (
                                      <span className="run-lineage-symbol-copy">
                                        Query plan {providerProvenanceSchedulerAlertHistory.search_summary.query_plan.join(" ")}
                                      </span>
                                    ) : null}
                                    <button
                                      className="ghost-button"
                                      disabled={!providerProvenanceSchedulerAlertTimelineItems.length}
                                      onClick={() => {
                                        void copyProviderProvenanceSchedulerStitchedNarrativeReport();
                                      }}
                                      type="button"
                                    >
                                      Copy stitched report
                                    </button>
                                    <button
                                      className="ghost-button"
                                      disabled={!providerProvenanceSchedulerAlertTimelineItems.length}
                                      onClick={() => {
                                        void downloadProviderProvenanceSchedulerStitchedNarrativeCsv();
                                      }}
                                      type="button"
                                    >
                                      Download stitched CSV
                                    </button>
                                    <button
                                      className="ghost-button"
                                      disabled={!providerProvenanceSchedulerAlertTimelineItems.length}
                                      onClick={() => {
                                        void shareProviderProvenanceSchedulerStitchedNarrativeReport();
                                      }}
                                      type="button"
                                    >
                                      Share stitched report
                                    </button>
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        stageProviderProvenanceSchedulerNarrativeDrafts();
                                      }}
                                      type="button"
                                    >
                                      Stage narrative drafts
                                    </button>
                                    <button
                                      className="ghost-button"
                                      disabled={!providerProvenanceSchedulerAlertHistory?.previous_offset && providerProvenanceSchedulerAlertHistoryOffset === 0}
                                      onClick={() => {
                                        setProviderProvenanceSchedulerAlertHistoryOffset(
                                          providerProvenanceSchedulerAlertHistory?.previous_offset ?? 0,
                                        );
                                      }}
                                      type="button"
                                    >
                                      Previous page
                                    </button>
                                    <button
                                      className="ghost-button"
                                      disabled={!(providerProvenanceSchedulerAlertHistory?.has_more ?? false)}
                                      onClick={() => {
                                        if (typeof providerProvenanceSchedulerAlertHistory?.next_offset === "number") {
                                          setProviderProvenanceSchedulerAlertHistoryOffset(
                                            providerProvenanceSchedulerAlertHistory.next_offset,
                                          );
                                        }
                                      }}
                                      type="button"
                                    >
                                      Next page
                                    </button>
                                    <span className="run-lineage-symbol-copy">
                                      {providerProvenanceSchedulerAlertHistory
                                        ? `${providerProvenanceSchedulerAlertHistory.query.offset + 1}-${providerProvenanceSchedulerAlertHistory.query.offset + providerProvenanceSchedulerAlertHistory.returned} of ${providerProvenanceSchedulerAlertHistory.total}`
                                        : "Page 1"}
                                    </span>
                                  </div>
                                  {providerProvenanceSchedulerAlertHistory?.search_analytics ? (
                                    <>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Scheduler search analytics</strong>
                                        <p>
                                          Query analytics, operator feedback, and learned tuning for the active
                                          scheduler narrative retrieval slice.
                                        </p>
                                      </div>
                                      <div className="run-filter-summary-chip-row">
                                        <span className="run-filter-summary-chip">
                                          Query {providerProvenanceSchedulerAlertHistory.search_analytics.query_id}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Recent runs {providerProvenanceSchedulerAlertHistory.search_analytics.recent_query_count}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Feedback {providerProvenanceSchedulerAlertHistory.search_analytics.relevant_feedback_count} relevant · {providerProvenanceSchedulerAlertHistory.search_analytics.not_relevant_feedback_count} not relevant
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Moderation pending {providerProvenanceSchedulerAlertHistory.search_analytics.pending_feedback_count} · approved {providerProvenanceSchedulerAlertHistory.search_analytics.approved_feedback_count} · rejected {providerProvenanceSchedulerAlertHistory.search_analytics.rejected_feedback_count}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Learned {providerProvenanceSchedulerAlertHistory.search_analytics.learned_relevance_active ? "active" : "cold"} · {providerProvenanceSchedulerAlertHistory.search_analytics.tuning_profile_version ?? "n/a"}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Channel Δ lexical {providerProvenanceSchedulerAlertHistory.search_analytics.channel_adjustments.lexical} · semantic {providerProvenanceSchedulerAlertHistory.search_analytics.channel_adjustments.semantic} · operator {providerProvenanceSchedulerAlertHistory.search_analytics.channel_adjustments.operator}
                                        </span>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Tuning</th>
                                            <th>Recent queries</th>
                                            <th>Recent feedback</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          <tr>
                                            <td>
                                              <strong>Field tuning</strong>
                                              <p className="run-lineage-symbol-copy">
                                                {providerProvenanceSchedulerAlertHistory.search_analytics.top_field_adjustments.length
                                                  ? providerProvenanceSchedulerAlertHistory.search_analytics.top_field_adjustments
                                                      .map((entry) => `${entry.field} ${entry.score > 0 ? "+" : ""}${entry.score}`)
                                                      .join(" · ")
                                                  : "No learned field adjustments yet."}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {providerProvenanceSchedulerAlertHistory.search_analytics.top_semantic_adjustments.length
                                                  ? providerProvenanceSchedulerAlertHistory.search_analytics.top_semantic_adjustments
                                                      .map((entry) => `${entry.concept} ${entry.score > 0 ? "+" : ""}${entry.score}`)
                                                      .join(" · ")
                                                  : "No learned semantic adjustments yet."}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {providerProvenanceSchedulerAlertHistory.search_analytics.top_operator_adjustments.length
                                                  ? providerProvenanceSchedulerAlertHistory.search_analytics.top_operator_adjustments
                                                      .map((entry) => `${entry.operator} ${entry.score > 0 ? "+" : ""}${entry.score}`)
                                                      .join(" · ")
                                                  : "No learned operator adjustments yet."}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>Recent queries</strong>
                                              {providerProvenanceSchedulerAlertHistory.search_analytics.recent_queries.length ? (
                                                providerProvenanceSchedulerAlertHistory.search_analytics.recent_queries.map((entry) => (
                                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-analytics-query-${entry.query_id}`}>
                                                    {entry.query} · top {entry.top_score} · {entry.matched_occurrences} match(es)
                                                  </p>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No persisted query analytics yet.</p>
                                              )}
                                            </td>
                                            <td>
                                              <strong>Recent feedback</strong>
                                              {providerProvenanceSchedulerAlertHistory.search_analytics.recent_feedback.length ? (
                                                providerProvenanceSchedulerAlertHistory.search_analytics.recent_feedback.map((entry) => (
                                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-feedback-${entry.feedback_id}`}>
                                                    {entry.occurrence_id} · {formatWorkflowToken(entry.signal)} · {formatWorkflowToken(entry.moderation_status)} · {entry.matched_fields.join(", ") || "ranked fields"}
                                                  </p>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No feedback recorded for this query yet.</p>
                                              )}
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </>
                                  ) : null}
                                  <div className="market-data-provenance-history-head">
                                    <strong>Scheduler query analytics dashboard</strong>
                                    <p>
                                      Moderate feedback before it influences learned ranking and inspect which
                                      scheduler search slices operators are using most often.
                                    </p>
                                  </div>
                                  <div className="market-data-provenance-history-actions">
                                    <label className="run-form-field">
                                      <span>Dashboard search</span>
                                      <input
                                        onChange={(event) => {
                                          setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                                            ...current,
                                            search: event.target.value,
                                          }));
                                        }}
                                        placeholder="query, occurrence id, actor, moderated by"
                                        type="search"
                                        value={providerProvenanceSchedulerSearchDashboardFilter.search}
                                      />
                                    </label>
                                    <label className="run-form-field">
                                      <span>Moderation</span>
                                      <select
                                        value={providerProvenanceSchedulerSearchDashboardFilter.moderation_status}
                                        onChange={(event) => {
                                          setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                                            ...current,
                                            moderation_status: event.target.value,
                                          }));
                                        }}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All states</option>
                                        <option value="pending">Pending</option>
                                        <option value="approved">Approved</option>
                                        <option value="rejected">Rejected</option>
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Signal</span>
                                      <select
                                        value={providerProvenanceSchedulerSearchDashboardFilter.signal}
                                        onChange={(event) => {
                                          setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                                            ...current,
                                            signal: event.target.value,
                                          }));
                                        }}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All signals</option>
                                        <option value="relevant">Relevant</option>
                                        <option value="not_relevant">Not relevant</option>
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Governance view</span>
                                      <select
                                        value={providerProvenanceSchedulerSearchDashboardFilter.governance_view}
                                        onChange={(event) => {
                                          setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                                            ...current,
                                            governance_view: event.target.value,
                                          }));
                                          setSelectedProviderProvenanceSchedulerSearchFeedbackIds([]);
                                        }}
                                      >
                                        <option value="all_feedback">All feedback</option>
                                        <option value="pending_queue">Pending queue</option>
                                        <option value="stale_pending">Stale pending</option>
                                        <option value="high_score_pending">High-score pending</option>
                                        <option value="moderated">Moderated</option>
                                        <option value="conflicting_queries">Conflicting queries</option>
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Window</span>
                                      <select
                                        value={providerProvenanceSchedulerSearchDashboardFilter.window_days}
                                        onChange={(event) => {
                                          setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                                            ...current,
                                            window_days: Number.parseInt(event.target.value, 10) || 30,
                                          }));
                                        }}
                                      >
                                        {[14, 30, 60, 90].map((value) => (
                                          <option key={`provider-scheduler-search-window-${value}`} value={value}>
                                            {value}d
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label className="run-form-field">
                                      <span>Stale pending</span>
                                      <select
                                        value={providerProvenanceSchedulerSearchDashboardFilter.stale_pending_hours}
                                        onChange={(event) => {
                                          setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                                            ...current,
                                            stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                                          }));
                                        }}
                                      >
                                        {[12, 24, 48, 72].map((value) => (
                                          <option key={`provider-scheduler-search-stale-${value}`} value={value}>
                                            {value}h
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    {providerProvenanceSchedulerSearchDashboard?.query.search ? (
                                      <span className="run-lineage-symbol-copy">
                                        Dashboard search {providerProvenanceSchedulerSearchDashboard.query.search}
                                      </span>
                                    ) : null}
                                  </div>
                                  {providerProvenanceSchedulerSearchDashboard ? (
                                    <>
                                      <div className="run-filter-summary-chip-row">
                                        <span className="run-filter-summary-chip">
                                          Queries {providerProvenanceSchedulerSearchDashboard.summary.query_count} · distinct {providerProvenanceSchedulerSearchDashboard.summary.distinct_query_count}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Feedback {providerProvenanceSchedulerSearchDashboard.summary.feedback_count} · pending {providerProvenanceSchedulerSearchDashboard.summary.pending_feedback_count}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Approved {providerProvenanceSchedulerSearchDashboard.summary.approved_feedback_count} · rejected {providerProvenanceSchedulerSearchDashboard.summary.rejected_feedback_count}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Signals {providerProvenanceSchedulerSearchDashboard.summary.relevant_feedback_count} relevant · {providerProvenanceSchedulerSearchDashboard.summary.not_relevant_feedback_count} not relevant
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Governance stale {providerProvenanceSchedulerSearchDashboard.moderation_governance.stale_pending_count} · high-score {providerProvenanceSchedulerSearchDashboard.moderation_governance.high_score_pending_count}
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Approval rate {providerProvenanceSchedulerSearchDashboard.moderation_governance.approval_rate_pct}% · conflicting queries {providerProvenanceSchedulerSearchDashboard.moderation_governance.conflicting_query_count}
                                        </span>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Long-horizon quality</th>
                                            <th>Actor rollup</th>
                                            <th>Moderator rollup</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          <tr>
                                            <td>
                                              <strong>
                                                {providerProvenanceSchedulerSearchDashboard.quality_dashboard.window_days} day trend
                                              </strong>
                                              {providerProvenanceSchedulerSearchDashboard.quality_dashboard.time_series.length ? (
                                                providerProvenanceSchedulerSearchDashboard.quality_dashboard.time_series
                                                  .slice(-6)
                                                  .map((entry) => (
                                                    <p
                                                      className="run-lineage-symbol-copy"
                                                      key={`provider-scheduler-search-quality-${entry.bucket_key}`}
                                                    >
                                                      {entry.bucket_label} · q {entry.query_count} · fb {entry.feedback_count} · pending {entry.pending_feedback_count} · approved {entry.approved_feedback_count}
                                                    </p>
                                                  ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No long-horizon scheduler search activity in the selected window.</p>
                                              )}
                                            </td>
                                            <td>
                                              <strong>Actors</strong>
                                              {providerProvenanceSchedulerSearchDashboard.quality_dashboard.actor_rollups.length ? (
                                                providerProvenanceSchedulerSearchDashboard.quality_dashboard.actor_rollups.map((entry) => (
                                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-actor-${entry.actor}`}>
                                                    {entry.actor} · {entry.feedback_count} feedback · pending {entry.pending_feedback_count} · relevant {entry.relevant_feedback_count}
                                                  </p>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No actor rollups for the current filter.</p>
                                              )}
                                            </td>
                                            <td>
                                              <strong>Moderators</strong>
                                              {providerProvenanceSchedulerSearchDashboard.quality_dashboard.moderator_rollups.length ? (
                                                providerProvenanceSchedulerSearchDashboard.quality_dashboard.moderator_rollups.map((entry) => (
                                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderator-${entry.moderated_by}`}>
                                                    {entry.moderated_by} · {entry.feedback_count} decisions · approved {entry.approved_feedback_count} · rejected {entry.rejected_feedback_count}
                                                  </p>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No moderator decisions recorded in the selected window.</p>
                                              )}
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Top queries</th>
                                            <th>Coverage</th>
                                            <th>Moderation</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          <tr>
                                            <td>
                                              <strong>Frequent searches</strong>
                                              {providerProvenanceSchedulerSearchDashboard.top_queries.length ? (
                                                providerProvenanceSchedulerSearchDashboard.top_queries.map((entry) => (
                                                  <div key={`provider-scheduler-search-dashboard-query-${entry.query_ids.join("-")}`}>
                                                    <p className="run-lineage-symbol-copy">
                                                      {entry.query} · {entry.search_count} run(s) · top {entry.top_score}
                                                    </p>
                                                    <div className="market-data-provenance-history-actions">
                                                      <button
                                                        className="ghost-button"
                                                        onClick={() => {
                                                          setProviderProvenanceAnalyticsQuery((current) => ({
                                                            ...current,
                                                            search_query: entry.query,
                                                          }));
                                                          setProviderProvenanceSchedulerAlertHistoryOffset(0);
                                                        }}
                                                        type="button"
                                                      >
                                                        Use query
                                                      </button>
                                                    </div>
                                                  </div>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No persisted scheduler search queries match the current dashboard filter.</p>
                                              )}
                                            </td>
                                            <td>
                                              <strong>Search footprint</strong>
                                              {providerProvenanceSchedulerSearchDashboard.top_queries.length ? (
                                                providerProvenanceSchedulerSearchDashboard.top_queries.map((entry) => (
                                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-dashboard-coverage-${entry.query_ids.join("-")}`}>
                                                    {entry.matched_occurrences_total} occurrence hit(s) · {entry.semantic_concepts.join(" · ") || "no semantic concepts"} · {entry.parsed_operators.join(" · ") || "no operators"}
                                                  </p>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">Coverage rolls up here once operators run scheduler searches.</p>
                                              )}
                                            </td>
                                            <td>
                                              <strong>Feedback counts</strong>
                                              {providerProvenanceSchedulerSearchDashboard.top_queries.length ? (
                                                providerProvenanceSchedulerSearchDashboard.top_queries.map((entry) => (
                                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-dashboard-feedback-${entry.query_ids.join("-")}`}>
                                                    pending {entry.pending_feedback_count} · approved {entry.approved_feedback_count} · rejected {entry.rejected_feedback_count}
                                                  </p>
                                                ))
                                              ) : (
                                                <p className="run-lineage-symbol-copy">No moderation queue activity for the current filter yet.</p>
                                              )}
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>
                                              <input
                                                checked={
                                                  providerProvenanceSchedulerSearchDashboard.feedback_items.length > 0
                                                  && providerProvenanceSchedulerSearchDashboard.feedback_items.every((entry) =>
                                                    selectedProviderProvenanceSchedulerSearchFeedbackIds.includes(entry.feedback_id),
                                                  )
                                                }
                                                onChange={(event) => {
                                                  setSelectedProviderProvenanceSchedulerSearchFeedbackIds(
                                                    event.target.checked
                                                      ? providerProvenanceSchedulerSearchDashboard.feedback_items.map((entry) => entry.feedback_id)
                                                      : [],
                                                  );
                                                }}
                                                type="checkbox"
                                              />
                                            </th>
                                            <th>Feedback item</th>
                                            <th>Signals</th>
                                            <th>Moderation</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchDashboard.feedback_items.length ? (
                                            providerProvenanceSchedulerSearchDashboard.feedback_items.map((entry) => (
                                              <tr key={`provider-scheduler-search-dashboard-feedback-item-${entry.feedback_id}`}>
                                                <td>
                                                  <input
                                                    checked={selectedProviderProvenanceSchedulerSearchFeedbackIds.includes(entry.feedback_id)}
                                                    onChange={(event) => {
                                                      setSelectedProviderProvenanceSchedulerSearchFeedbackIds((current) =>
                                                        event.target.checked
                                                          ? [...current, entry.feedback_id]
                                                          : current.filter((feedbackId) => feedbackId !== entry.feedback_id),
                                                      );
                                                    }}
                                                    type="checkbox"
                                                  />
                                                </td>
                                                <td>
                                                  <strong>{entry.query}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.occurrence_id} · {formatWorkflowToken(entry.signal)} · score {entry.score}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.matched_fields.join(" · ") || "ranked fields"} · {entry.semantic_concepts.join(" · ") || "no semantic concepts"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Age {entry.age_hours}h · query runs {entry.query_run_count}
                                                  </p>
                                                  {entry.note ? (
                                                    <p className="run-lineage-symbol-copy">{entry.note}</p>
                                                  ) : null}
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.moderation_status)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Recorded {formatTimestamp(entry.recorded_at)} · actor {entry.actor ?? "operator"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Moderated {formatTimestamp(entry.moderated_at ?? null)} · by {entry.moderated_by ?? "n/a"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.stale_pending ? "Stale pending" : "Fresh queue"} · {entry.high_score_pending ? "high-score" : "normal-score"}
                                                  </p>
                                                  {entry.moderation_note ? (
                                                    <p className="run-lineage-symbol-copy">{entry.moderation_note}</p>
                                                  ) : null}
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      disabled={providerProvenanceSchedulerSearchFeedbackModerationPendingId === entry.feedback_id}
                                                      onClick={() => {
                                                        void moderateProviderProvenanceSchedulerSearchFeedbackEntry(entry.feedback_id, "approved");
                                                      }}
                                                      type="button"
                                                    >
                                                      Approve
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={providerProvenanceSchedulerSearchFeedbackModerationPendingId === entry.feedback_id}
                                                      onClick={() => {
                                                        void moderateProviderProvenanceSchedulerSearchFeedbackEntry(entry.feedback_id, "rejected");
                                                      }}
                                                      type="button"
                                                    >
                                                      Reject
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={providerProvenanceSchedulerSearchFeedbackModerationPendingId === entry.feedback_id}
                                                      onClick={() => {
                                                        void moderateProviderProvenanceSchedulerSearchFeedbackEntry(entry.feedback_id, "pending");
                                                      }}
                                                      type="button"
                                                    >
                                                      Queue
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={4}>
                                                <p className="empty-state">
                                                  No scheduler search feedback matches the current moderation filter.
                                                </p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                      <div className="market-data-provenance-history-actions">
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                                            || providerProvenanceSchedulerSearchFeedbackModerationPendingId !== null
                                          }
                                          onClick={() => {
                                            void moderateProviderProvenanceSchedulerSearchFeedbackSelection("approved");
                                          }}
                                          type="button"
                                        >
                                          Approve selected
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                                            || providerProvenanceSchedulerSearchFeedbackModerationPendingId !== null
                                          }
                                          onClick={() => {
                                            void moderateProviderProvenanceSchedulerSearchFeedbackSelection("rejected");
                                          }}
                                          type="button"
                                        >
                                          Reject selected
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                                            || providerProvenanceSchedulerSearchFeedbackModerationPendingId !== null
                                          }
                                          onClick={() => {
                                            void moderateProviderProvenanceSchedulerSearchFeedbackSelection("pending");
                                          }}
                                          type="button"
                                        >
                                          Queue selected
                                        </button>
                                        <span className="run-lineage-symbol-copy">
                                          {selectedProviderProvenanceSchedulerSearchFeedbackIds.length} selected
                                        </span>
                                      </div>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Scheduler moderation policy catalogs</strong>
                                        <p>
                                          Save reusable moderation defaults and route selected feedback through a staged
                                          approval queue before it changes learned ranking.
                                        </p>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <label className="run-form-field">
                                          <span>Name</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                name: event.target.value,
                                              }));
                                            }}
                                            placeholder="Pending scheduler approvals"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.name}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Description</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                description: event.target.value,
                                              }));
                                            }}
                                            placeholder="Moderate high-signal scheduler feedback before tuning"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.description}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Default outcome</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.default_moderation_status}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                default_moderation_status: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="approved">Approved</option>
                                            <option value="rejected">Rejected</option>
                                            <option value="pending">Pending</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Governance view</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.governance_view}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                governance_view: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="pending_queue">Pending queue</option>
                                            <option value="stale_pending">Stale pending</option>
                                            <option value="high_score_pending">High-score pending</option>
                                            <option value="conflicting_queries">Conflicting queries</option>
                                            <option value="all_feedback">All feedback</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Window</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.window_days}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                window_days: Number.parseInt(event.target.value, 10) || 30,
                                              }));
                                            }}
                                          >
                                            {[14, 30, 60, 90].map((value) => (
                                              <option key={`provider-scheduler-search-policy-window-${value}`} value={value}>
                                                {value}d
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Stale pending</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.stale_pending_hours}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                                              }));
                                            }}
                                          >
                                            {[12, 24, 48, 72].map((value) => (
                                              <option key={`provider-scheduler-search-policy-stale-${value}`} value={value}>
                                                {value}h
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Minimum score</span>
                                          <input
                                            min={0}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                minimum_score: Math.max(Number.parseInt(event.target.value, 10) || 0, 0),
                                              }));
                                            }}
                                            type="number"
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.minimum_score}
                                          />
                                        </label>
                                        <label className="run-form-field checkbox-field">
                                          <span>Require note</span>
                                          <input
                                            checked={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.require_note}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                                                ...current,
                                                require_note: event.target.checked,
                                              }));
                                            }}
                                            type="checkbox"
                                          />
                                        </label>
                                        <button
                                          className="ghost-button"
                                          disabled={providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading}
                                          onClick={() => {
                                            void createProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry();
                                          }}
                                          type="button"
                                        >
                                          {editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? "Update policy catalog" : "Save policy catalog"}
                                        </button>
                                        {editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? (
                                          <button
                                            className="ghost-button"
                                            onClick={() => {
                                              resetProviderProvenanceSchedulerSearchModerationPolicyCatalogEditor();
                                              setProviderProvenanceWorkspaceFeedback("Moderation policy catalog editor reset.");
                                            }}
                                            type="button"
                                          >
                                            Cancel edit
                                          </button>
                                        ) : null}
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <span className="run-lineage-symbol-copy">
                                          {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length} selected
                                        </span>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                                            || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
                                          }
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("delete");
                                          }}
                                          type="button"
                                        >
                                          Delete selected
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                                            || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
                                          }
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("restore");
                                          }}
                                          type="button"
                                        >
                                          Restore selected
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                                            || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
                                          }
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("update");
                                          }}
                                          type="button"
                                        >
                                          Bulk edit
                                        </button>
                                        <label className="run-form-field">
                                          <span>Name prefix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }));
                                            }}
                                            placeholder="[Ops] "
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.name_prefix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Name suffix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }));
                                            }}
                                            placeholder=" / reviewed"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.name_suffix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Description append</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                description_append: event.target.value,
                                              }));
                                            }}
                                            placeholder="Bulk-governed in control room"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.description_append}
                                          />
                                        </label>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>
                                              <input
                                                aria-label="Select all moderation policy catalogs"
                                                checked={
                                                  (providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ?? 0) > 0
                                                  && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                                                    === (providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ?? 0)
                                                }
                                                onChange={toggleAllProviderProvenanceSchedulerSearchModerationPolicyCatalogSelections}
                                                type="checkbox"
                                              />
                                            </th>
                                            <th>Catalog</th>
                                            <th>Defaults</th>
                                            <th>Governance</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ? (
                                            providerProvenanceSchedulerSearchModerationPolicyCatalogs.items.map((entry) => (
                                              <tr key={`provider-scheduler-search-policy-catalog-${entry.catalog_id}`}>
                                                <td className="provider-provenance-selection-cell">
                                                  <input
                                                    aria-label={`Select moderation policy catalog ${entry.name}`}
                                                    checked={selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.includes(entry.catalog_id)}
                                                    onChange={() => {
                                                      toggleProviderProvenanceSchedulerSearchModerationPolicyCatalogSelection(entry.catalog_id);
                                                    }}
                                                    type="checkbox"
                                                  />
                                                </td>
                                                <td>
                                                  <strong>{entry.name}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.description || "No description"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {shortenIdentifier(entry.catalog_id, 10)} · created {formatTimestamp(entry.created_at)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                                                    {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                                                  </p>
                                                </td>
                                                <td>
                                                  <p className="run-lineage-symbol-copy">
                                                    Outcome {formatWorkflowToken(entry.default_moderation_status)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Minimum score {entry.minimum_score} · note {entry.require_note ? "required" : "optional"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <p className="run-lineage-symbol-copy">
                                                    View {formatWorkflowToken(entry.governance_view)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Window {entry.window_days}d · stale {entry.stale_pending_hours}h
                                                  </p>
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void editProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry(entry);
                                                      }}
                                                      type="button"
                                                    >
                                                      Edit
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void deleteProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry(entry);
                                                      }}
                                                      type="button"
                                                    >
                                                      Delete
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        if (
                                                          selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId === entry.catalog_id
                                                          && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory
                                                        ) {
                                                          setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId(null);
                                                          setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory(null);
                                                          setProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryError(null);
                                                        } else {
                                                          void loadProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory(entry.catalog_id);
                                                        }
                                                      }}
                                                      type="button"
                                                    >
                                                      {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId === entry.catalog_id
                                                        && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory
                                                        ? "Hide versions"
                                                        : "Versions"}
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={5}>
                                                <p className="empty-state">
                                                  No scheduler moderation policy catalogs saved yet.
                                                </p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                      {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? (
                                        <div className="market-data-provenance-shared-history">
                                          <div className="market-data-provenance-history-head">
                                            <strong>Scheduler moderation policy catalog revisions</strong>
                                            <p>Inspect immutable catalog snapshots and restore a previous moderation governance revision.</p>
                                          </div>
                                          {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryLoading ? (
                                            <p className="empty-state">Loading moderation policy catalog revisions…</p>
                                          ) : null}
                                          {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError ? (
                                            <p className="market-data-workflow-feedback">
                                              Moderation policy catalog revisions failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError}
                                            </p>
                                          ) : null}
                                          {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory ? (
                                            <table className="data-table">
                                              <thead>
                                                <tr>
                                                  <th>When</th>
                                                  <th>Snapshot</th>
                                                  <th>Action</th>
                                                </tr>
                                              </thead>
                                              <tbody>
                                                {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory.history.map((entry) => (
                                                  <tr key={entry.revision_id}>
                                                    <td>
                                                      <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                      <p className="run-lineage-symbol-copy">
                                                        {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                                                      </p>
                                                    </td>
                                                    <td>
                                                      <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                                                      <p className="run-lineage-symbol-copy">{entry.name}</p>
                                                      <p className="run-lineage-symbol-copy">
                                                        Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">
                                                        Window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">{entry.reason}</p>
                                                    </td>
                                                    <td>
                                                      <button
                                                        className="ghost-button"
                                                        onClick={() => {
                                                          void restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryRevision(entry.revision_id);
                                                        }}
                                                        type="button"
                                                      >
                                                        Restore revision
                                                      </button>
                                                    </td>
                                                  </tr>
                                                ))}
                                              </tbody>
                                            </table>
                                          ) : null}
                                        </div>
                                      ) : null}
                                      <div className="market-data-provenance-shared-history">
                                        <div className="market-data-provenance-history-head">
                                          <strong>Scheduler moderation policy catalog team audit</strong>
                                          <p>Filter lifecycle and bulk-governance events by catalog, action, actor, or search text.</p>
                                        </div>
                                        <div className="filter-bar">
                                          <label>
                                            <span>Catalog</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                                                  ...current,
                                                  catalog_id: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.catalog_id}
                                            >
                                              <option value="">All catalogs</option>
                                              {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                                                <option key={entry.catalog_id} value={entry.catalog_id}>
                                                  {entry.name}
                                                </option>
                                              ))}
                                            </select>
                                          </label>
                                          <label>
                                            <span>Action</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                                                  ...current,
                                                  action: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.action}
                                            >
                                              <option value={ALL_FILTER_VALUE}>All actions</option>
                                              <option value="created">Created</option>
                                              <option value="updated">Updated</option>
                                              <option value="deleted">Deleted</option>
                                              <option value="restored">Restored</option>
                                              <option value="bulk_updated">Bulk updated</option>
                                              <option value="bulk_deleted">Bulk deleted</option>
                                              <option value="bulk_restored">Bulk restored</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Actor tab</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                                                  ...current,
                                                  actor_tab_id: event.target.value,
                                                }))
                                              }
                                              placeholder="control-room"
                                              type="text"
                                              value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.actor_tab_id}
                                            />
                                          </label>
                                          <label>
                                            <span>Search</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                                                  ...current,
                                                  search: event.target.value,
                                                }))
                                              }
                                              placeholder="high-score pending"
                                              type="text"
                                              value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.search}
                                            />
                                          </label>
                                        </div>
                                        {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading ? (
                                          <p className="empty-state">Loading scheduler moderation policy catalog audit…</p>
                                        ) : null}
                                        {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError ? (
                                          <p className="market-data-workflow-feedback">
                                            Scheduler moderation policy catalog audit failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError}
                                          </p>
                                        ) : null}
                                        {providerProvenanceSchedulerSearchModerationPolicyCatalogAudits.length ? (
                                          <table className="data-table">
                                            <thead>
                                              <tr>
                                                <th>When</th>
                                                <th>Action</th>
                                                <th>Detail</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {providerProvenanceSchedulerSearchModerationPolicyCatalogAudits.map((entry) => (
                                                <tr key={entry.audit_id}>
                                                  <td>
                                                    <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      {entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <strong>{formatWorkflowToken(entry.action)}</strong>
                                                    <p className="run-lineage-symbol-copy">{entry.name}</p>
                                                    <p className="run-lineage-symbol-copy">
                                                      {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.default_moderation_status)}
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <p className="run-lineage-symbol-copy">{entry.detail}</p>
                                                    <p className="run-lineage-symbol-copy">
                                                      View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                                                    </p>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        ) : (
                                          !providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading ? (
                                            <p className="empty-state">No moderation policy catalog audit rows match the current filter.</p>
                                          ) : null
                                        )}
                                      </div>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Moderation catalog governance policies</strong>
                                        <p>
                                          Save reusable approval requirements and update defaults, then stage
                                          selected moderation policy catalogs through a dedicated governance queue.
                                        </p>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <label className="run-form-field">
                                          <span>Name</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                name: event.target.value,
                                              }));
                                            }}
                                            placeholder="Catalog cleanup with approval"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Action scope</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.action_scope}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                action_scope: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="any">Any action</option>
                                            <option value="update">Update only</option>
                                            <option value="delete">Delete only</option>
                                            <option value="restore">Restore only</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field checkbox-field">
                                          <span>Require approval note</span>
                                          <input
                                            checked={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.require_approval_note}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                require_approval_note: event.target.checked,
                                              }));
                                            }}
                                            type="checkbox"
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Description</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                description: event.target.value,
                                              }));
                                            }}
                                            placeholder="Stage policy-catalog changes behind explicit approval."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.description}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Guidance</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                guidance: event.target.value,
                                              }));
                                            }}
                                            placeholder="Require note before catalog lifecycle changes."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.guidance}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Name prefix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }));
                                            }}
                                            placeholder="[Ops] "
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name_prefix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Name suffix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }));
                                            }}
                                            placeholder=" / reviewed"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name_suffix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Description append</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                description_append: event.target.value,
                                              }));
                                            }}
                                            placeholder=" Escalate stale pending rows before applying."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.description_append}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Default outcome</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.default_moderation_status}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                default_moderation_status: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="approved">Approved</option>
                                            <option value="rejected">Rejected</option>
                                            <option value="pending">Pending</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Governance view</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.governance_view}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                governance_view: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="pending_queue">Pending queue</option>
                                            <option value="stale_pending">Stale pending</option>
                                            <option value="high_score_pending">High-score pending</option>
                                            <option value="conflicting_queries">Conflicting queries</option>
                                            <option value="all_feedback">All feedback</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Window</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.window_days}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                window_days: Number.parseInt(event.target.value, 10) || 30,
                                              }));
                                            }}
                                          >
                                            {[14, 30, 60, 90].map((value) => (
                                              <option key={`provider-scheduler-search-governance-policy-window-${value}`} value={value}>
                                                {value}d
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Stale pending</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.stale_pending_hours}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                                              }));
                                            }}
                                          >
                                            {[12, 24, 48, 72].map((value) => (
                                              <option key={`provider-scheduler-search-governance-policy-stale-${value}`} value={value}>
                                                {value}h
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Minimum score</span>
                                          <input
                                            min={0}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                minimum_score: Math.max(Number.parseInt(event.target.value, 10) || 0, 0),
                                              }));
                                            }}
                                            type="number"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.minimum_score}
                                          />
                                        </label>
                                        <label className="run-form-field checkbox-field">
                                          <span>Require moderation note</span>
                                          <input
                                            checked={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.require_note}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                                                ...current,
                                                require_note: event.target.checked,
                                              }));
                                            }}
                                            type="checkbox"
                                          />
                                        </label>
                                        <button
                                          className="ghost-button"
                                          disabled={providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading}
                                          onClick={() => {
                                            void createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry();
                                          }}
                                          type="button"
                                        >
                                          {editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? "Update governance policy" : "Save governance policy"}
                                        </button>
                                        {editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? (
                                          <button
                                            className="ghost-button"
                                            onClick={() => {
                                              resetProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEditor();
                                              setProviderProvenanceWorkspaceFeedback("Moderation governance policy editor reset.");
                                            }}
                                            type="button"
                                          >
                                            Cancel edit
                                          </button>
                                        ) : null}
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <span className="run-lineage-symbol-copy">
                                          {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length} selected
                                        </span>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                                            || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
                                          }
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("delete");
                                          }}
                                          type="button"
                                        >
                                          Delete selected
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                                            || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
                                          }
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("restore");
                                          }}
                                          type="button"
                                        >
                                          Restore selected
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                                            || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
                                          }
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("update");
                                          }}
                                          type="button"
                                        >
                                          Bulk edit
                                        </button>
                                        <label className="run-form-field">
                                          <span>Name prefix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }));
                                            }}
                                            placeholder="[Ops] "
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.name_prefix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Name suffix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }));
                                            }}
                                            placeholder=" / reviewed"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.name_suffix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Guidance</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                                                ...current,
                                                guidance: event.target.value,
                                              }));
                                            }}
                                            placeholder="Require explicit review before apply."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.guidance}
                                          />
                                        </label>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>
                                              <input
                                                aria-label="Select all moderation governance policies"
                                                checked={
                                                  (providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ?? 0) > 0
                                                  && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                                                    === (providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ?? 0)
                                                }
                                                onChange={toggleAllProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelections}
                                                type="checkbox"
                                              />
                                            </th>
                                            <th>Policy</th>
                                            <th>Defaults</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ? (
                                            providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies.items.map((entry) => (
                                              <tr key={`provider-scheduler-search-moderation-governance-policy-${entry.governance_policy_id}`}>
                                                <td className="provider-provenance-selection-cell">
                                                  <input
                                                    aria-label={`Select moderation governance policy ${entry.name}`}
                                                    checked={selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.includes(entry.governance_policy_id)}
                                                    onChange={() => {
                                                      toggleProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelection(entry.governance_policy_id);
                                                    }}
                                                    type="checkbox"
                                                  />
                                                </td>
                                                <td>
                                                  <strong>{entry.name}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.action_scope)} · approval note {entry.require_approval_note ? "required" : "optional"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.guidance || entry.description || "No governance guidance"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                                                    {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                                                  </p>
                                                </td>
                                                <td>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.name_prefix || entry.name_suffix
                                                      ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                                                      : "No name affixes"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                                                  </p>
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void editProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry(entry);
                                                      }}
                                                      type="button"
                                                    >
                                                      Edit
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry(entry);
                                                      }}
                                                      type="button"
                                                    >
                                                      Delete
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        if (
                                                          selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId === entry.governance_policy_id
                                                          && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory
                                                        ) {
                                                          setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId(null);
                                                          setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory(null);
                                                          setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError(null);
                                                        } else {
                                                          void loadProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory(entry.governance_policy_id);
                                                        }
                                                      }}
                                                      type="button"
                                                    >
                                                      {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId === entry.governance_policy_id
                                                        && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory
                                                        ? "Hide versions"
                                                        : "Versions"}
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                                                          ...current,
                                                          governance_policy_id: entry.governance_policy_id,
                                                          action:
                                                            entry.action_scope === "update"
                                                            || entry.action_scope === "delete"
                                                            || entry.action_scope === "restore"
                                                              ? entry.action_scope
                                                              : current.action,
                                                        }));
                                                        setProviderProvenanceWorkspaceFeedback(
                                                          `Selected moderation catalog governance policy ${entry.name}.`,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Use policy
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={4}>
                                                <p className="empty-state">No moderation catalog governance policies saved yet.</p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                      {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? (
                                        <div className="market-data-provenance-shared-history">
                                          <div className="market-data-provenance-history-head">
                                            <strong>Moderation governance policy revisions</strong>
                                            <p>Inspect immutable policy snapshots and restore a previous governance default set.</p>
                                          </div>
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryLoading ? (
                                            <p className="empty-state">Loading moderation governance policy revisions…</p>
                                          ) : null}
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError ? (
                                            <p className="market-data-workflow-feedback">
                                              Moderation governance policy revisions failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError}
                                            </p>
                                          ) : null}
                                          {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory ? (
                                            <table className="data-table">
                                              <thead>
                                                <tr>
                                                  <th>When</th>
                                                  <th>Snapshot</th>
                                                  <th>Action</th>
                                                </tr>
                                              </thead>
                                              <tbody>
                                                {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory.history.map((entry) => (
                                                  <tr key={entry.revision_id}>
                                                    <td>
                                                      <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                      <p className="run-lineage-symbol-copy">
                                                        {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                                                      </p>
                                                    </td>
                                                    <td>
                                                      <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                                                      <p className="run-lineage-symbol-copy">{entry.name}</p>
                                                      <p className="run-lineage-symbol-copy">
                                                        {formatWorkflowToken(entry.action_scope)} · approval note {entry.require_approval_note ? "required" : "optional"}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">
                                                        Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">{entry.reason}</p>
                                                    </td>
                                                    <td>
                                                      <button
                                                        className="ghost-button"
                                                        onClick={() => {
                                                          void restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRevision(entry.revision_id);
                                                        }}
                                                        type="button"
                                                      >
                                                        Restore revision
                                                      </button>
                                                    </td>
                                                  </tr>
                                                ))}
                                              </tbody>
                                            </table>
                                          ) : null}
                                        </div>
                                      ) : null}
                                      <div className="market-data-provenance-shared-history">
                                        <div className="market-data-provenance-history-head">
                                          <strong>Moderation governance policy team audit</strong>
                                          <p>Filter lifecycle and bulk governance events by policy, action, actor, or search text.</p>
                                        </div>
                                        <div className="filter-bar">
                                          <label>
                                            <span>Policy</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                                                  ...current,
                                                  governance_policy_id: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.governance_policy_id}
                                            >
                                              <option value="">All policies</option>
                                              {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                                                <option key={entry.governance_policy_id} value={entry.governance_policy_id}>
                                                  {entry.name}
                                                </option>
                                              ))}
                                            </select>
                                          </label>
                                          <label>
                                            <span>Action</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                                                  ...current,
                                                  action: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.action}
                                            >
                                              <option value={ALL_FILTER_VALUE}>All actions</option>
                                              <option value="created">Created</option>
                                              <option value="updated">Updated</option>
                                              <option value="deleted">Deleted</option>
                                              <option value="restored">Restored</option>
                                              <option value="bulk_updated">Bulk updated</option>
                                              <option value="bulk_deleted">Bulk deleted</option>
                                              <option value="bulk_restored">Bulk restored</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Actor tab</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                                                  ...current,
                                                  actor_tab_id: event.target.value,
                                                }))
                                              }
                                              placeholder="control-room"
                                              type="text"
                                              value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.actor_tab_id}
                                            />
                                          </label>
                                          <label>
                                            <span>Search</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                                                  ...current,
                                                  search: event.target.value,
                                                }))
                                              }
                                              placeholder="approval note"
                                              type="text"
                                              value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.search}
                                            />
                                          </label>
                                        </div>
                                        {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading ? (
                                          <p className="empty-state">Loading moderation governance policy audit…</p>
                                        ) : null}
                                        {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError ? (
                                          <p className="market-data-workflow-feedback">
                                            Moderation governance policy audit failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError}
                                          </p>
                                        ) : null}
                                        {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits.length ? (
                                          <table className="data-table">
                                            <thead>
                                              <tr>
                                                <th>When</th>
                                                <th>Action</th>
                                                <th>Detail</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits.map((entry) => (
                                                <tr key={entry.audit_id}>
                                                  <td>
                                                    <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      {entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <strong>{formatWorkflowToken(entry.action)}</strong>
                                                    <p className="run-lineage-symbol-copy">{entry.name}</p>
                                                    <p className="run-lineage-symbol-copy">
                                                      {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.action_scope)}
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <p className="run-lineage-symbol-copy">{entry.detail}</p>
                                                    <p className="run-lineage-symbol-copy">
                                                      View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                                                    </p>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        ) : (
                                          !providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading ? (
                                            <p className="empty-state">No moderation governance policy audit rows match the current filter.</p>
                                          ) : null
                                        )}
                                      </div>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Moderation governance meta-policies</strong>
                                        <p>
                                          Save reusable review defaults for moderation governance policies, then
                                          stage selected policy updates through a dedicated approval queue.
                                        </p>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <label className="run-form-field">
                                          <span>Name</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                name: event.target.value,
                                              }));
                                            }}
                                            placeholder="Review moderation governance defaults"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Queue action</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.action_scope}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                action_scope: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="any">Any action</option>
                                            <option value="update">Update only</option>
                                            <option value="delete">Delete only</option>
                                            <option value="restore">Restore only</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Policy action</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_action_scope}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                policy_action_scope: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="any">Any action</option>
                                            <option value="update">Update only</option>
                                            <option value="delete">Delete only</option>
                                            <option value="restore">Restore only</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field checkbox-field">
                                          <span>Approval note</span>
                                          <input
                                            checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_approval_note}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                require_approval_note: event.target.checked,
                                              }));
                                            }}
                                            type="checkbox"
                                          />
                                        </label>
                                        <label className="run-form-field checkbox-field">
                                          <span>Policy note</span>
                                          <input
                                            checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_require_approval_note}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                policy_require_approval_note: event.target.checked,
                                              }));
                                            }}
                                            type="checkbox"
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Description</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                description: event.target.value,
                                              }));
                                            }}
                                            placeholder="Reusable defaults for moderation governance policy review."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Queue guidance</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                guidance: event.target.value,
                                              }));
                                            }}
                                            placeholder="Require an explicit note before approval."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.guidance}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Policy guidance</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                policy_guidance: event.target.value,
                                              }));
                                            }}
                                            placeholder="Apply these defaults to selected governance policies."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_guidance}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Name prefix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }));
                                            }}
                                            placeholder="[Reviewed] "
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_prefix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Name suffix</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }));
                                            }}
                                            placeholder=" / approved"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_suffix}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Description append</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                description_append: event.target.value,
                                              }));
                                            }}
                                            placeholder=" Reviewed in moderation governance queue."
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description_append}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Outcome</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.default_moderation_status}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                default_moderation_status: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="approved">Approved</option>
                                            <option value="pending">Pending</option>
                                            <option value="rejected">Rejected</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Governance view</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.governance_view}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                governance_view: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="all_feedback">All feedback</option>
                                            <option value="pending_queue">Pending queue</option>
                                            <option value="high_score_pending">High-score pending</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Window days</span>
                                          <input
                                            min={7}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                window_days: Number(event.target.value) || 0,
                                              }));
                                            }}
                                            type="number"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.window_days}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Stale pending hours</span>
                                          <input
                                            min={1}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                stale_pending_hours: Number(event.target.value) || 0,
                                              }));
                                            }}
                                            type="number"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.stale_pending_hours}
                                          />
                                        </label>
                                        <label className="run-form-field">
                                          <span>Minimum score</span>
                                          <input
                                            min={0}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                minimum_score: Number(event.target.value) || 0,
                                              }));
                                            }}
                                            type="number"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.minimum_score}
                                          />
                                        </label>
                                        <label className="run-form-field checkbox-field">
                                          <span>Require moderator note</span>
                                          <input
                                            checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_note}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                                                ...current,
                                                require_note: event.target.checked,
                                              }));
                                            }}
                                            type="checkbox"
                                          />
                                        </label>
                                        <button
                                          className="ghost-button"
                                          disabled={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesLoading}
                                          onClick={() => {
                                            void createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry();
                                          }}
                                          type="button"
                                        >
                                          Save meta-policy
                                        </button>
                                      </div>
                                      {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError ? (
                                        <p className="market-data-workflow-feedback">
                                          Moderation governance meta-policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError}
                                        </p>
                                      ) : null}
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Meta-policy</th>
                                            <th>Defaults</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items.length ? (
                                            providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies.items.map((entry) => (
                                              <tr key={`provider-scheduler-search-moderation-governance-meta-policy-${entry.meta_policy_id}`}>
                                                <td>
                                                  <strong>{entry.name}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Queue {formatWorkflowToken(entry.action_scope)} · note {entry.require_approval_note ? "required" : "optional"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.guidance || entry.description || "No meta-governance guidance"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Saved {formatTimestamp(entry.updated_at)} · {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <p className="run-lineage-symbol-copy">
                                                    Policy {formatWorkflowToken(entry.policy_action_scope ?? "any")} · note {entry.policy_require_approval_note ? "required" : "optional"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Outcome {formatWorkflowToken(entry.default_moderation_status ?? "approved")} · view {formatWorkflowToken(entry.governance_view ?? "pending_queue")}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Window {entry.window_days ?? 0}d · stale {entry.stale_pending_hours ?? 0}h · minimum {entry.minimum_score ?? 0}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.name_prefix || entry.name_suffix
                                                      ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                                                      : "No name affixes"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDefaults(entry);
                                                      }}
                                                      type="button"
                                                    >
                                                      Use defaults
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={3}>
                                                <p className="empty-state">No moderation governance meta-policies saved yet.</p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Moderation governance approval queue</strong>
                                        <p>
                                          Stage selected moderation governance policies, preview the exact policy diffs,
                                          then approve and apply the change set.
                                        </p>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <label className="run-form-field">
                                          <span>Action</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.action}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                                                ...current,
                                                action: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="update">Update</option>
                                            <option value="delete">Delete</option>
                                            <option value="restore">Restore</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Reusable meta-policy</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.meta_policy_id}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                                                ...current,
                                                meta_policy_id: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>Inline policy patch</option>
                                            {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items ?? []).map((entry) => (
                                              <option key={`provider-scheduler-search-moderation-governance-meta-policy-option-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Approval/apply note</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                                                ...current,
                                                note: event.target.value,
                                              }));
                                            }}
                                            placeholder="required when the meta-policy gates approval on notes"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.note}
                                          />
                                        </label>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                                            || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId !== null
                                          }
                                          onClick={() => {
                                            void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaSelection();
                                          }}
                                          type="button"
                                        >
                                          Stage selected policies
                                        </button>
                                        <label className="run-form-field">
                                          <span>Queue state</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.queue_state}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                                                ...current,
                                                queue_state: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All states</option>
                                            <option value="pending_approval">Pending approval</option>
                                            <option value="ready_to_apply">Ready to apply</option>
                                            <option value="completed">Completed</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Meta-policy</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.meta_policy_id}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                                                ...current,
                                                meta_policy_id: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All meta-policies</option>
                                            {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.available_filters.meta_policies ?? []).map((entry) => (
                                              <option key={`provider-scheduler-search-moderation-governance-meta-plan-policy-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <span className="run-lineage-symbol-copy">
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.completed_count ?? 0} completed
                                        </span>
                                      </div>
                                      {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError ? (
                                        <p className="market-data-workflow-feedback">
                                          Moderation governance approval queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError}
                                        </p>
                                      ) : null}
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Plan</th>
                                            <th>Preview</th>
                                            <th>Queue</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.items.length ? (
                                            providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans.items.map((entry) => (
                                              <tr key={`provider-scheduler-search-moderation-governance-meta-plan-${entry.plan_id}`}>
                                                <td>
                                                  <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.action)} · {entry.meta_policy_name ?? "Inline defaults"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                                                  </p>
                                                  {entry.guidance ? (
                                                    <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                                                  ) : null}
                                                </td>
                                                <td>
                                                  <strong>{entry.preview_count} preview item(s)</strong>
                                                  {entry.preview_items.slice(0, 4).map((preview) => (
                                                    <div key={`provider-scheduler-search-moderation-governance-meta-preview-${entry.plan_id}-${preview.governance_policy_id}`}>
                                                      <p className="run-lineage-symbol-copy">
                                                        {preview.governance_policy_name} · {formatWorkflowToken(preview.outcome)}
                                                        {preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                                                        {preview.message ? ` · ${preview.message}` : ""}
                                                      </p>
                                                      {Object.entries(preview.field_diffs).slice(0, 2).map(([field, diff]) => (
                                                        <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-governance-meta-diff-${entry.plan_id}-${preview.governance_policy_id}-${field}`}>
                                                          {field}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.before)} → {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.after)}
                                                        </p>
                                                      ))}
                                                    </div>
                                                  ))}
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                                                  </p>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      disabled={
                                                        entry.queue_state !== "pending_approval"
                                                        || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                                                      }
                                                      onClick={() => {
                                                        void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                                                      }}
                                                      type="button"
                                                    >
                                                      Approve
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={
                                                        entry.queue_state !== "ready_to_apply"
                                                        || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                                                      }
                                                      onClick={() => {
                                                        void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                                                      }}
                                                      type="button"
                                                    >
                                                      Apply
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={3}>
                                                <p className="empty-state">No moderation governance meta-plans match the current filter.</p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Moderation catalog governance queue</strong>
                                        <p>
                                          Stage selected moderation policy catalogs, preview the exact catalog diffs,
                                          then approve and apply the change set.
                                        </p>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <label className="run-form-field">
                                          <span>Action</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.action}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                                                ...current,
                                                action: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="update">Update</option>
                                            <option value="delete">Delete</option>
                                            <option value="restore">Restore</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Governance policy</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.governance_policy_id}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                                                ...current,
                                                governance_policy_id: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>No reusable policy</option>
                                            {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                                              <option key={`provider-scheduler-search-moderation-governance-policy-option-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Approval/apply note</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                                                ...current,
                                                note: event.target.value,
                                              }));
                                            }}
                                            placeholder="required when the governance policy gates approval on notes"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.note}
                                          />
                                        </label>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                                            || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId !== null
                                          }
                                          onClick={() => {
                                            void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceSelection();
                                          }}
                                          type="button"
                                        >
                                          Stage selected catalogs
                                        </button>
                                        <label className="run-form-field">
                                          <span>Queue state</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.queue_state}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                                                ...current,
                                                queue_state: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All states</option>
                                            <option value="pending_approval">Pending approval</option>
                                            <option value="ready_to_apply">Ready to apply</option>
                                            <option value="completed">Completed</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Governance policy</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.governance_policy_id}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                                                ...current,
                                                governance_policy_id: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All policies</option>
                                            {(providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.available_filters.governance_policies ?? []).map((entry) => (
                                              <option key={`provider-scheduler-search-moderation-governance-queue-policy-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <span className="run-lineage-symbol-copy">
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.completed_count ?? 0} completed
                                        </span>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Plan</th>
                                            <th>Preview</th>
                                            <th>Queue</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.items.length ? (
                                            providerProvenanceSchedulerSearchModerationCatalogGovernancePlans.items.map((entry) => (
                                              <tr key={`provider-scheduler-search-moderation-catalog-governance-plan-${entry.plan_id}`}>
                                                <td>
                                                  <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.action)} · {entry.governance_policy_name ?? "No policy"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                                                  </p>
                                                  {entry.guidance ? (
                                                    <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                                                  ) : null}
                                                </td>
                                                <td>
                                                  <strong>{entry.preview_count} preview item(s)</strong>
                                                  {entry.preview_items.slice(0, 4).map((preview) => (
                                                    <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-catalog-governance-preview-${entry.plan_id}-${preview.catalog_id}`}>
                                                      {preview.catalog_name} · {formatWorkflowToken(preview.outcome)}{preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                                                      {preview.message ? ` · ${preview.message}` : ""}
                                                    </p>
                                                  ))}
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                                                  </p>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      disabled={
                                                        entry.queue_state !== "pending_approval"
                                                        || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                                                      }
                                                      onClick={() => {
                                                        void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                                                      }}
                                                      type="button"
                                                    >
                                                      Approve
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={
                                                        entry.queue_state !== "ready_to_apply"
                                                        || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                                                      }
                                                      onClick={() => {
                                                        void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                                                      }}
                                                      type="button"
                                                    >
                                                      Apply
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={3}>
                                                <p className="empty-state">No moderation catalog governance plans match the current filter.</p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Scheduler moderation approval queue</strong>
                                        <p>
                                          Stage selected feedback, review the plan preview, then approve and apply it
                                          as a governed moderation batch.
                                        </p>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <label className="run-form-field">
                                          <span>Stage policy catalog</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationStageDraft.policy_catalog_id}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                                                ...current,
                                                policy_catalog_id: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>No catalog</option>
                                            {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                                              <option key={`provider-scheduler-search-stage-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Fallback outcome</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationStageDraft.moderation_status}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                                                ...current,
                                                moderation_status: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value="approved">Approved</option>
                                            <option value="rejected">Rejected</option>
                                            <option value="pending">Pending</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Approval/apply note</span>
                                          <input
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                                                ...current,
                                                note: event.target.value,
                                              }));
                                            }}
                                            placeholder="required by policy catalogs that gate approval on notes"
                                            type="text"
                                            value={providerProvenanceSchedulerSearchModerationStageDraft.note}
                                          />
                                        </label>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                                            || providerProvenanceSchedulerSearchModerationPlanPendingId !== null
                                          }
                                          onClick={() => {
                                            void stageProviderProvenanceSchedulerSearchModerationSelection();
                                          }}
                                          type="button"
                                        >
                                          Stage selected feedback
                                        </button>
                                        <label className="run-form-field">
                                          <span>Queue state</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationQueueFilter.queue_state}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                                                ...current,
                                                queue_state: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All states</option>
                                            <option value="pending_approval">Pending approval</option>
                                            <option value="ready_to_apply">Ready to apply</option>
                                            <option value="completed">Completed</option>
                                          </select>
                                        </label>
                                        <label className="run-form-field">
                                          <span>Policy catalog</span>
                                          <select
                                            value={providerProvenanceSchedulerSearchModerationQueueFilter.policy_catalog_id}
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                                                ...current,
                                                policy_catalog_id: event.target.value,
                                              }));
                                            }}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All catalogs</option>
                                            {(providerProvenanceSchedulerSearchModerationPlans?.available_filters.policy_catalogs ?? []).map((entry) => (
                                              <option key={`provider-scheduler-search-queue-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <span className="run-lineage-symbol-copy">
                                          {providerProvenanceSchedulerSearchModerationPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationPlans?.summary.completed_count ?? 0} completed
                                        </span>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Plan</th>
                                            <th>Preview</th>
                                            <th>Queue</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerSearchModerationPlans?.items.length ? (
                                            providerProvenanceSchedulerSearchModerationPlans.items.map((entry) => (
                                              <tr key={`provider-scheduler-search-moderation-plan-${entry.plan_id}`}>
                                                <td>
                                                  <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.policy_catalog_name ?? "No catalog"} · {formatWorkflowToken(entry.proposed_moderation_status)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Eligible {entry.feedback_ids.length}/{entry.requested_feedback_ids.length} · minimum score {entry.minimum_score}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{entry.preview_count} preview item(s)</strong>
                                                  {entry.preview_items.slice(0, 4).map((preview) => (
                                                    <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-preview-${entry.plan_id}-${preview.feedback_id}`}>
                                                      {preview.occurrence_id} · {formatWorkflowToken(preview.current_moderation_status)} → {formatWorkflowToken(preview.proposed_moderation_status)} · score {preview.score} · {preview.eligible ? "eligible" : "skipped"}
                                                      {preview.reason_tags.length ? ` · ${preview.reason_tags.join(" · ")}` : ""}
                                                    </p>
                                                  ))}
                                                  {entry.missing_feedback_ids.length ? (
                                                    <p className="run-lineage-symbol-copy">
                                                      Missing {entry.missing_feedback_ids.join(" · ")}
                                                    </p>
                                                  ) : null}
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                                                  </p>
                                                  {entry.approval_note ? (
                                                    <p className="run-lineage-symbol-copy">{entry.approval_note}</p>
                                                  ) : null}
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      disabled={
                                                        entry.queue_state !== "pending_approval"
                                                        || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                                                      }
                                                      onClick={() => {
                                                        void approveProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                                                      }}
                                                      type="button"
                                                    >
                                                      Approve
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={
                                                        entry.queue_state !== "ready_to_apply"
                                                        || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                                                      }
                                                      onClick={() => {
                                                        void applyProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                                                      }}
                                                      type="button"
                                                    >
                                                      Apply
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))
                                          ) : (
                                            <tr>
                                              <td colSpan={3}>
                                                <p className="empty-state">
                                                  No staged scheduler moderation plans match the current queue filter.
                                                </p>
                                              </td>
                                            </tr>
                                          )}
                                        </tbody>
                                      </table>
                                    </>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchDashboardLoading ? (
                                    <p className="empty-state">Loading scheduler search dashboard…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchDashboardError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduler search dashboard failed: {providerProvenanceSchedulerSearchDashboardError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading
                                  || providerProvenanceSchedulerSearchModerationPlansLoading
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernancePlansLoading ? (
                                    <p className="empty-state">Loading scheduler moderation governance…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchModerationPolicyCatalogsError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduler moderation policy catalogs failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogsError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduler moderation catalog governance policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduler moderation catalog governance queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerSearchModerationPlansError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduler moderation approval queue failed: {providerProvenanceSchedulerSearchModerationPlansError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerAlertRetrievalClusters.length ? (
                                    <>
                                      <div className="market-data-provenance-history-head">
                                        <strong>Cross-occurrence retrieval clusters</strong>
                                        <p>
                                          Semantic/vector clustering groups related scheduler occurrences across the
                                          current search slice so review can start from recovery or failure narratives
                                          instead of single rows.
                                        </p>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Cluster</th>
                                            <th>Coverage</th>
                                            <th>Signals</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerAlertRetrievalClusters.map((cluster) => (
                                            <tr key={`provider-scheduler-retrieval-cluster-${cluster.cluster_id ?? cluster.rank}`}>
                                              <td>
                                                <strong>{cluster.label ?? `Cluster ${cluster.rank}`}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  Rank {cluster.rank} · {cluster.occurrence_count} occurrence(s)
                                                </p>
                                                {cluster.top_occurrence_summary ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Top occurrence {cluster.top_occurrence_summary}
                                                  </p>
                                                ) : null}
                                              </td>
                                              <td>
                                                <strong>Top {cluster.top_score}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  Avg {cluster.average_score} · similarity {cluster.average_similarity_pct}%
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {cluster.summary ?? "Cross-occurrence retrieval cluster"}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>
                                                  {cluster.semantic_concepts.length
                                                    ? cluster.semantic_concepts.join(" · ")
                                                    : "No dominant semantic concept"}
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  Vector {cluster.vector_terms.join(" · ") || "n/a"}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {cluster.categories.join(" · ") || "n/a"} · {cluster.statuses.join(" · ") || "n/a"}
                                                </p>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </>
                                  ) : null}
                                  {providerProvenanceSchedulerAlertHistoryLoading && !providerProvenanceSchedulerAlertTimelineItems.length ? (
                                    <p className="empty-state">Loading scheduler alert timeline…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerAlertHistoryError ? (
                                    <p className="market-data-workflow-feedback">
                                      Scheduler alert timeline failed: {providerProvenanceSchedulerAlertHistoryError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerAlertTimelineItems.length ? (
                                    <table className="data-table">
                                      <thead>
                                        <tr>
                                          <th>Occurrence</th>
                                          <th>Window</th>
                                          <th>Summary</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {providerProvenanceSchedulerAlertTimelineItems.map((alert) => {
                                          const timelineSummary = formatProviderProvenanceSchedulerTimelineSummary(alert);
                                          const narrativeFacetLabel = formatProviderProvenanceSchedulerNarrativeFacet(
                                            alert.narrative.facet ?? "all_occurrences",
                                          );
                                          return (
                                            <tr key={`provider-scheduler-alert-timeline-${getOperatorAlertOccurrenceKey(alert)}`}>
                                              <td>
                                                <strong>{formatWorkflowToken(alert.category)}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(alert.status)} · {alert.severity}
                                                </p>
                                                {timelineSummary ? (
                                                  <p className="run-lineage-symbol-copy">{timelineSummary}</p>
                                                ) : null}
                                                <p className="run-lineage-symbol-copy">
                                                  Narrative {narrativeFacetLabel} · {alert.narrative.occurrence_record_count} occurrence record(s)
                                                </p>
                                              </td>
                                              <td>
                                                <strong>{formatTimestamp(alert.detected_at)}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  Resolved {formatTimestamp(alert.resolved_at ?? null)}
                                                </p>
                                                {alert.occurrence_id ? (
                                                  <p className="run-lineage-symbol-copy">{alert.occurrence_id}</p>
                                                ) : null}
                                                {alert.search_match ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatProviderProvenanceSchedulerSearchMatchSummary(alert.search_match)}
                                                  </p>
                                                ) : null}
                                                {alert.retrieval_cluster ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatProviderProvenanceSchedulerRetrievalClusterSummary(alert.retrieval_cluster)}
                                                  </p>
                                                ) : null}
                                                {alert.narrative.can_reconstruct_narrative ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Sequence {alert.narrative.status_sequence.join(" → ") || "n/a"}
                                                  </p>
                                                ) : null}
                                              </td>
                                              <td>
                                                <strong>{alert.summary}</strong>
                                                <p className="run-lineage-symbol-copy">{alert.detail}</p>
                                                <p className="run-lineage-symbol-copy">
                                                  Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {alert.narrative.can_reconstruct_narrative
                                                    ? `Narrative mode ${formatWorkflowToken(alert.narrative.narrative_mode ?? "mixed_status_post_resolution")} · post-resolution ${alert.narrative.post_resolution_record_count} record(s)`
                                                    : "Active occurrence uses the current scheduler snapshot until it resolves."}
                                                </p>
                                                {alert.narrative.has_post_resolution_history ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Post-resolution sequence {alert.narrative.post_resolution_status_sequence.join(" → ") || "n/a"} · window ended {formatTimestamp(alert.narrative.narrative_window_ended_at ?? null)}
                                                  </p>
                                                ) : null}
                                                {alert.narrative.next_occurrence_detected_at ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Next recurrence detected {formatTimestamp(alert.narrative.next_occurrence_detected_at)}
                                                  </p>
                                                ) : null}
                                                {alert.search_match?.highlights.length ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Match {alert.search_match.highlights.join(" · ")}
                                                  </p>
                                                ) : null}
                                                {alert.search_match?.operator_hits.length ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Operators {alert.search_match.operator_hits.join(" · ")}
                                                  </p>
                                                ) : null}
                                                {alert.search_match?.semantic_concepts.length ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Semantic {alert.search_match.semantic_concepts.join(" · ")}
                                                  </p>
                                                ) : null}
                                                {alert.search_match?.ranking_reason ? (
                                                  <p className="run-lineage-symbol-copy">{alert.search_match.ranking_reason}</p>
                                                ) : null}
                                                {alert.search_match?.relevance_model ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Relevance {alert.search_match.relevance_model} · lexical {alert.search_match.lexical_score} · semantic {alert.search_match.semantic_score} · operator {alert.search_match.operator_score} · learned {alert.search_match.learned_score}
                                                  </p>
                                                ) : null}
                                                {alert.search_match?.tuning_signals.length ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Learned signals {alert.search_match.tuning_signals.join(" · ")}
                                                  </p>
                                                ) : null}
                                                {alert.retrieval_cluster?.vector_terms.length ? (
                                                  <p className="run-lineage-symbol-copy">
                                                    Cluster vector {alert.retrieval_cluster.vector_terms.join(" · ")}
                                                  </p>
                                                ) : null}
                                                <div className="market-data-provenance-history-actions">
                                                  {alert.search_match && providerProvenanceSchedulerAlertHistory?.search_summary?.query_id ? (
                                                    <>
                                                      <button
                                                        className="ghost-button"
                                                        disabled={
                                                          providerProvenanceSchedulerSearchFeedbackPendingOccurrenceKey === getOperatorAlertOccurrenceKey(alert)
                                                        }
                                                        onClick={() => {
                                                          void submitProviderProvenanceSchedulerSearchFeedback(alert, "relevant");
                                                        }}
                                                        type="button"
                                                      >
                                                        Relevant
                                                      </button>
                                                      <button
                                                        className="ghost-button"
                                                        disabled={
                                                          providerProvenanceSchedulerSearchFeedbackPendingOccurrenceKey === getOperatorAlertOccurrenceKey(alert)
                                                        }
                                                        onClick={() => {
                                                          void submitProviderProvenanceSchedulerSearchFeedback(alert, "not_relevant");
                                                        }}
                                                        type="button"
                                                      >
                                                        Not relevant
                                                      </button>
                                                    </>
                                                  ) : null}
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                                                        sourceLabel: `${alert.summary} scheduler timeline row`,
                                                      });
                                                    }}
                                                    type="button"
                                                  >
                                                    {alert.status === "resolved" ? "Reconstruct narrative export" : "Start current workflow"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                                                        escalate: true,
                                                        sourceLabel: `${alert.summary} scheduler timeline row`,
                                                      });
                                                    }}
                                                    type="button"
                                                  >
                                                    {alert.status === "resolved"
                                                      ? "Escalate narrative export"
                                                      : "Escalate current snapshot"}
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          );
                                        })}
                                      </tbody>
                                    </table>
                                  ) : (
                                    <p className="empty-state">No scheduler alert occurrences match the selected filters.</p>
                                  )}
                                  <div className="market-data-provenance-history-head">
                                    <strong>Saved stitched report views</strong>
                                    <p>
                                      Store stitched multi-occurrence scheduler report slices as reusable saved views,
                                      then re-apply, copy, download, or share them without rebuilding the filter set by
                                      hand.
                                    </p>
                                  </div>
                                  <div className="filter-bar">
                                    <label>
                                      <span>Name</span>
                                      <input
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerStitchedReportViewDraft((current) => ({
                                            ...current,
                                            name: event.target.value,
                                          }))
                                        }
                                        placeholder="Lag recovery stitched report"
                                        type="text"
                                        value={providerProvenanceSchedulerStitchedReportViewDraft.name}
                                      />
                                    </label>
                                    <label>
                                      <span>Description</span>
                                      <input
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerStitchedReportViewDraft((current) => ({
                                            ...current,
                                            description: event.target.value,
                                          }))
                                        }
                                        placeholder="saved stitched occurrence slice"
                                        type="text"
                                        value={providerProvenanceSchedulerStitchedReportViewDraft.description}
                                      />
                                    </label>
                                    <label>
                                      <span>Action</span>
                                      <div className="market-data-provenance-history-actions">
                                        <button
                                          className="ghost-button"
                                          onClick={() => {
                                            void saveCurrentProviderProvenanceSchedulerStitchedReportView();
                                          }}
                                          type="button"
                                        >
                                          {editingProviderProvenanceSchedulerStitchedReportViewId
                                            ? "Save changes"
                                            : "Save stitched view"}
                                        </button>
                                        {editingProviderProvenanceSchedulerStitchedReportViewId ? (
                                          <button
                                            className="ghost-button"
                                            onClick={() => {
                                              resetProviderProvenanceSchedulerStitchedReportViewDraft();
                                            }}
                                            type="button"
                                          >
                                            Cancel edit
                                          </button>
                                        ) : null}
                                      </div>
                                    </label>
                                  </div>
                                  {providerProvenanceSchedulerStitchedReportViews.length ? (
                                    <div className="provider-provenance-governance-bar">
                                      <div className="provider-provenance-governance-summary">
                                        <strong>
                                          {selectedProviderProvenanceSchedulerStitchedReportViewIds.length} selected
                                        </strong>
                                        <span>
                                          {selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter((entry) => entry.status === "active").length} active · {" "}
                                          {selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter((entry) => entry.status === "deleted").length} deleted
                                        </span>
                                      </div>
                                      <div className="market-data-provenance-history-actions">
                                        <button
                                          className="ghost-button"
                                          onClick={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
                                          type="button"
                                        >
                                          {selectedProviderProvenanceSchedulerStitchedReportViewIds.length === providerProvenanceSchedulerStitchedReportViews.length
                                            ? "Clear all"
                                            : "Select all"}
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={!selectedProviderProvenanceSchedulerStitchedReportViewIds.length || providerProvenanceSchedulerStitchedReportViewBulkAction !== null}
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("delete");
                                          }}
                                          type="button"
                                        >
                                          {providerProvenanceSchedulerStitchedReportViewBulkAction === "delete"
                                            ? "Previewing…"
                                            : "Preview delete"}
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={!selectedProviderProvenanceSchedulerStitchedReportViewIds.length || providerProvenanceSchedulerStitchedReportViewBulkAction !== null}
                                          onClick={() => {
                                            void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("restore");
                                          }}
                                          type="button"
                                        >
                                          {providerProvenanceSchedulerStitchedReportViewBulkAction === "restore"
                                            ? "Previewing…"
                                            : "Preview restore"}
                                        </button>
                                      </div>
                                    </div>
                                  ) : null}
                                  {providerProvenanceSchedulerStitchedReportViews.length ? (
                                    <div className="provider-provenance-governance-editor">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Bulk stitched view edits</strong>
                                        <p>Preview metadata, scheduler slice filters, and export-limit changes across multiple saved stitched report views, then approve and apply the staged plan.</p>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Name prefix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }))
                                            }
                                            placeholder="Ops / "
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.name_prefix}
                                          />
                                        </label>
                                        <label>
                                          <span>Name suffix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }))
                                            }
                                            placeholder=" / v2"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.name_suffix}
                                          />
                                        </label>
                                        <label>
                                          <span>Description append</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                description_append: event.target.value,
                                              }))
                                            }
                                            placeholder="reviewed in shift handoff"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.description_append}
                                          />
                                        </label>
                                        <label>
                                          <span>Category</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                scheduler_alert_category: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_category}
                                          >
                                            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                            <option value={ALL_FILTER_VALUE}>All categories</option>
                                            <option value="scheduler_lag">scheduler lag</option>
                                            <option value="scheduler_failure">scheduler failure</option>
                                          </select>
                                        </label>
                                        <label>
                                          <span>Status</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                scheduler_alert_status: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_status}
                                          >
                                            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                            <option value={ALL_FILTER_VALUE}>All statuses</option>
                                            <option value="active">active</option>
                                            <option value="resolved">resolved</option>
                                          </select>
                                        </label>
                                        <label>
                                          <span>Facet</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                scheduler_alert_narrative_facet:
                                                  event.target.value === "resolved_narratives"
                                                  || event.target.value === "post_resolution_recovery"
                                                  || event.target.value === "recurring_occurrences"
                                                  || event.target.value === "all_occurrences"
                                                    ? event.target.value
                                                    : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_narrative_facet}
                                          >
                                            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                            <option value="all_occurrences">all occurrences</option>
                                            <option value="resolved_narratives">resolved narratives</option>
                                            <option value="post_resolution_recovery">post-resolution recovery</option>
                                            <option value="recurring_occurrences">recurring occurrences</option>
                                          </select>
                                        </label>
                                        <label>
                                          <span>Window days</span>
                                          <input
                                            inputMode="numeric"
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                window_days: event.target.value,
                                              }))
                                            }
                                            placeholder="keep"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.window_days}
                                          />
                                        </label>
                                        <label>
                                          <span>Result limit</span>
                                          <input
                                            inputMode="numeric"
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                result_limit: event.target.value,
                                              }))
                                            }
                                            placeholder="keep"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.result_limit}
                                          />
                                        </label>
                                        <label>
                                          <span>Occurrence limit</span>
                                          <input
                                            inputMode="numeric"
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                occurrence_limit: event.target.value,
                                              }))
                                            }
                                            placeholder="keep"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.occurrence_limit}
                                          />
                                        </label>
                                        <label>
                                          <span>History limit</span>
                                          <input
                                            inputMode="numeric"
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                history_limit: event.target.value,
                                              }))
                                            }
                                            placeholder="keep"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.history_limit}
                                          />
                                        </label>
                                        <label>
                                          <span>Drill-down limit</span>
                                          <input
                                            inputMode="numeric"
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                                                ...current,
                                                drilldown_history_limit: event.target.value,
                                              }))
                                            }
                                            placeholder="keep"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportViewBulkDraft.drilldown_history_limit}
                                          />
                                        </label>
                                        <label>
                                          <span>Policy template</span>
                                          <select
                                            onChange={(event) => {
                                              setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId(
                                                event.target.value,
                                              );
                                            }}
                                            value={providerProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId}
                                          >
                                            <option value="">Default staged policy</option>
                                            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                                              .filter(
                                                (entry) =>
                                                  entry.status === "active"
                                                  && providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                                                    entry.item_type_scope,
                                                    "stitched_report_view",
                                                  ),
                                              )
                                              .map((entry) => (
                                                <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                  {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                                                </option>
                                              ))}
                                          </select>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <div className="market-data-provenance-history-actions">
                                            <button
                                              className="ghost-button"
                                              disabled={!selectedProviderProvenanceSchedulerStitchedReportViewIds.length || providerProvenanceSchedulerStitchedReportViewBulkAction !== null}
                                              onClick={() => {
                                                void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("update");
                                              }}
                                              type="button"
                                            >
                                              {providerProvenanceSchedulerStitchedReportViewBulkAction === "update"
                                                ? "Previewing…"
                                                : "Preview bulk edit"}
                                            </button>
                                          </div>
                                        </label>
                                      </div>
                                    </div>
                                  ) : null}
                                  {providerProvenanceSchedulerStitchedReportViewsLoading ? (
                                    <p className="empty-state">Loading stitched report views…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerStitchedReportViewsError ? (
                                    <p className="market-data-workflow-feedback">
                                      Stitched report views failed: {providerProvenanceSchedulerStitchedReportViewsError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerStitchedReportViews.length ? (
                                    <table className="data-table">
                                      <thead>
                                        <tr>
                                          <th>
                                            <input
                                              aria-label="Select all stitched report views"
                                              checked={
                                                providerProvenanceSchedulerStitchedReportViews.length > 0
                                                && selectedProviderProvenanceSchedulerStitchedReportViewIds.length === providerProvenanceSchedulerStitchedReportViews.length
                                              }
                                              onChange={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
                                              type="checkbox"
                                            />
                                          </th>
                                          <th>View</th>
                                          <th>Slice</th>
                                          <th>Action</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {providerProvenanceSchedulerStitchedReportViews.map((entry) => (
                                          <tr key={`provider-scheduler-stitched-view-${entry.view_id}`}>
                                            <td className="provider-provenance-selection-cell">
                                              <input
                                                aria-label={`Select stitched report view ${entry.name}`}
                                                checked={selectedProviderProvenanceSchedulerStitchedReportViewIdSet.has(entry.view_id)}
                                                onChange={() => {
                                                  toggleProviderProvenanceSchedulerStitchedReportViewSelection(entry.view_id);
                                                }}
                                                type="checkbox"
                                              />
                                            </td>
                                            <td>
                                              <strong>{entry.name}</strong>
                                              <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"} · updated{" "}
                                                {formatTimestamp(entry.updated_at)}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                                                {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{entry.occurrence_limit} occurrence(s)</strong>
                                              <p className="run-lineage-symbol-copy">
                                                History {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                Focus {entry.query.focus_scope === "current_focus" ? "current focus" : "all focuses"}
                                              </p>
                                            </td>
                                            <td>
                                              <div className="market-data-provenance-history-actions">
                                                <button
                                                  className="ghost-button"
                                                  disabled={entry.status !== "active"}
                                                  onClick={() => {
                                                    void applyProviderProvenanceSchedulerStitchedReportView(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Apply
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  disabled={entry.status !== "active"}
                                                  onClick={() => {
                                                    void editProviderProvenanceSchedulerStitchedReportView(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Edit
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  disabled={entry.status !== "active"}
                                                  onClick={() => {
                                                    void deleteProviderProvenanceSchedulerStitchedReportViewEntry(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Delete
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void toggleProviderProvenanceSchedulerStitchedReportViewHistory(entry.view_id);
                                                  }}
                                                  type="button"
                                                >
                                                  {selectedProviderProvenanceSchedulerStitchedReportViewId === entry.view_id
                                                    && selectedProviderProvenanceSchedulerStitchedReportViewHistory
                                                    ? "Hide versions"
                                                    : "Versions"}
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void copyProviderProvenanceSchedulerStitchedNarrativeReportView(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Copy report
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void downloadProviderProvenanceSchedulerStitchedNarrativeCsvView(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Download CSV
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void shareProviderProvenanceSchedulerStitchedNarrativeReportView(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Share report
                                                </button>
                                              </div>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  ) : (
                                    <p className="empty-state">No stitched scheduler report views saved yet.</p>
                                  )}
                                  {selectedProviderProvenanceSchedulerStitchedReportViewId ? (
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Stitched report view revisions</strong>
                                        <p>Inspect immutable saved-view snapshots, apply them to the workbench, or restore them as the active stitched report view.</p>
                                      </div>
                                      {providerProvenanceSchedulerStitchedReportViewHistoryLoading ? (
                                        <p className="empty-state">Loading stitched report view revisions…</p>
                                      ) : null}
                                      {providerProvenanceSchedulerStitchedReportViewHistoryError ? (
                                        <p className="market-data-workflow-feedback">
                                          Stitched report view revisions failed: {providerProvenanceSchedulerStitchedReportViewHistoryError}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceSchedulerStitchedReportViewHistory ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>When</th>
                                              <th>Snapshot</th>
                                              <th>Action</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {selectedProviderProvenanceSchedulerStitchedReportViewHistory.history.map((entry) => (
                                              <tr key={entry.revision_id}>
                                                <td>
                                                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                                                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.occurrence_limit} occurrence(s) · history {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">{entry.reason}</p>
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        void applyProviderProvenanceWorkspaceQuery(entry, {
                                                          includeLayout: false,
                                                          forceSchedulerHighlight: true,
                                                          feedbackLabel: `Stitched report revision ${entry.revision_id}`,
                                                        });
                                                      }}
                                                      type="button"
                                                    >
                                                      Apply snapshot
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        void restoreProviderProvenanceSchedulerStitchedReportViewHistoryRevision(entry);
                                                      }}
                                                      type="button"
                                                    >
                                                      Restore revision
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : null}
                                    </div>
                                  ) : null}
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Stitched report view team audit</strong>
                                      <p>Filter shared audit rows by saved view, action, or actor to review bulk governance and lifecycle changes.</p>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>View</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                                              ...current,
                                              view_id: event.target.value,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportViewAuditFilter.view_id}
                                        >
                                          <option value="">All views</option>
                                          {providerProvenanceSchedulerStitchedReportViews.map((entry) => (
                                            <option key={entry.view_id} value={entry.view_id}>
                                              {entry.name}
                                            </option>
                                          ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Action</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                                              ...current,
                                              action: event.target.value,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportViewAuditFilter.action}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All actions</option>
                                          <option value="created">Created</option>
                                          <option value="updated">Updated</option>
                                          <option value="deleted">Deleted</option>
                                          <option value="restored">Restored</option>
                                        </select>
                                      </label>
                                      <label>
                                        <span>Actor tab</span>
                                        <input
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                                              ...current,
                                              actor_tab_id: event.target.value,
                                            }))
                                          }
                                          placeholder="tab_ops"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportViewAuditFilter.actor_tab_id}
                                        />
                                      </label>
                                      <label>
                                        <span>Search</span>
                                        <input
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                                              ...current,
                                              search: event.target.value,
                                            }))
                                          }
                                          placeholder="lag recovery"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportViewAuditFilter.search}
                                        />
                                      </label>
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportViewAuditsLoading ? (
                                      <p className="empty-state">Loading stitched report view audit…</p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportViewAuditsError ? (
                                      <p className="market-data-workflow-feedback">
                                        Stitched report view audit failed: {providerProvenanceSchedulerStitchedReportViewAuditsError}
                                      </p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportViewAudits.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>When</th>
                                            <th>Action</th>
                                            <th>Actor</th>
                                            <th>Detail</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerStitchedReportViewAudits.map((entry) => (
                                            <tr key={`provider-scheduler-stitched-view-audit-${entry.audit_id}`}>
                                              <td>
                                                <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                <p className="run-lineage-symbol-copy">{entry.name}</p>
                                              </td>
                                              <td>
                                                <strong>{formatWorkflowToken(entry.action)}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(entry.status)} · {entry.filter_summary}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.actor_tab_id ?? "No tab id recorded."}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>{entry.detail}</strong>
                                                <p className="run-lineage-symbol-copy">{entry.reason}</p>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.occurrence_limit} occurrence(s) · history {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                                                </p>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                  ) : (
                                      !providerProvenanceSchedulerStitchedReportViewAuditsLoading
                                        ? <p className="empty-state">No stitched report view audit events match the selected filters.</p>
                                        : null
                                    )}
                                  </div>
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Stitched report approval queue</strong>
                                      <p>
                                        Review saved stitched report view governance plans without leaving the stitched
                                        report surface. This keeps stitched-report approvals and policy defaults visible
                                        next to the saved lens they change.
                                      </p>
                                    </div>
                                    <div className="provider-provenance-governance-summary">
                                      <strong>
                                        {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.total} stitched plan(s)
                                      </strong>
                                      <span>
                                        {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.pending_approval_count} pending approval · {" "}
                                        {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.ready_to_apply_count} ready to apply · {" "}
                                        {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.completed_count} completed
                                      </span>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>Queue state</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              queue_state:
                                                event.target.value === "pending_approval"
                                                || event.target.value === "ready_to_apply"
                                                || event.target.value === "completed"
                                                  ? event.target.value
                                                  : ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.queue_state}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All states</option>
                                          <option value="pending_approval">Pending approval</option>
                                          <option value="ready_to_apply">Ready to apply</option>
                                          <option value="completed">Completed</option>
                                        </select>
                                      </label>
                                      <label>
                                        <span>Lane</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              approval_lane: event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.approval_lane}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All lanes</option>
                                          {Array.from(
                                            new Set(
                                              providerProvenanceSchedulerStitchedReportGovernancePlans.map(
                                                (entry) => entry.approval_lane,
                                              ),
                                            ),
                                          ).sort().map((lane) => (
                                            <option key={lane} value={lane}>
                                              {formatWorkflowToken(lane)}
                                            </option>
                                          ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Priority</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              approval_priority: event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.approval_priority}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All priorities</option>
                                          <option value="low">Low</option>
                                          <option value="normal">Normal</option>
                                          <option value="high">High</option>
                                          <option value="critical">Critical</option>
                                        </select>
                                      </label>
                                      <label>
                                        <span>Policy template</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              policy_template_id:
                                                event.target.value === ""
                                                  ? ""
                                                  : event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_template_id}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All policy templates</option>
                                          <option value="">No policy template</option>
                                          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                                            .filter(
                                              (entry) =>
                                                providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                                                  entry.item_type_scope,
                                                  "stitched_report_view",
                                                ),
                                            )
                                            .map((entry) => (
                                              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Policy catalog</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              policy_catalog_id:
                                                event.target.value === ""
                                                  ? ""
                                                  : event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_catalog_id}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
                                          <option value="">No policy catalog</option>
                                          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
                                            <option key={entry.catalog_id} value={entry.catalog_id}>
                                              {entry.name}
                                            </option>
                                          ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Search</span>
                                        <input
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              search: event.target.value,
                                            }))
                                          }
                                          placeholder="plan, view, policy"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.search}
                                        />
                                      </label>
                                      <label>
                                        <span>Sort</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                                              ...current,
                                              sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                                                event.target.value,
                                              ),
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.sort}
                                        >
                                          <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
                                            Queue priority
                                          </option>
                                          <option value="updated_desc">Updated newest</option>
                                          <option value="updated_asc">Updated oldest</option>
                                          <option value="created_desc">Created newest</option>
                                          <option value="created_asc">Created oldest</option>
                                        </select>
                                      </label>
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportGovernancePlansLoading ? (
                                      <p className="empty-state">Loading stitched report approval queue…</p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernancePlansError ? (
                                      <p className="market-data-workflow-feedback">
                                        Stitched report approval queue failed: {providerProvenanceSchedulerStitchedReportGovernancePlansError}
                                      </p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernancePlans.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Plan</th>
                                            <th>Preview</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerStitchedReportGovernancePlans.map((plan) => (
                                            <tr key={`provider-scheduler-stitched-governance-plan-${plan.plan_id}`}>
                                              <td>
                                                <strong>
                                                  {formatWorkflowToken(plan.action)} stitched_report_view
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}
                                                  {plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}
                                                  {plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
                                                </p>
                                                {plan.policy_guidance ? (
                                                  <p className="run-lineage-symbol-copy">{plan.policy_guidance}</p>
                                                ) : null}
                                              </td>
                                              <td>
                                                <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
                                                <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
                                                <p className="run-lineage-symbol-copy">
                                                  {plan.preview_items.length} preview row(s) · rollback ready {plan.rollback_ready_count}
                                                </p>
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
                                                      ? "Shared queue selected"
                                                      : "Review in shared queue"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={
                                                      plan.status !== "previewed"
                                                      || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                                    }
                                                    onClick={() => {
                                                      void approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
                                                      ? "Approving…"
                                                      : "Approve"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={
                                                      plan.status !== "approved"
                                                      || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                                    }
                                                    onClick={() => {
                                                      void applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
                                                      ? "Applying…"
                                                      : "Apply"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={
                                                      plan.status !== "applied"
                                                      || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                                    }
                                                    onClick={() => {
                                                      void rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
                                                      ? "Rolling back…"
                                                      : "Rollback"}
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : (
                                      !providerProvenanceSchedulerStitchedReportGovernancePlansLoading
                                        ? <p className="empty-state">No stitched report governance plans match the dedicated queue filters.</p>
                                        : null
                                    )}
                                  </div>
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Stitched report policy catalogs</strong>
                                      <p>
                                        Review only governance catalogs that can drive stitched report view approval
                                        defaults, then apply those defaults or jump into the shared catalog workspace.
                                      </p>
                                    </div>
                                    <div className="provider-provenance-governance-summary">
                                      <strong>
                                        {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length} stitched catalog(s)
                                      </strong>
                                      <span>
                                        {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter((entry) => entry.status === "active").length} active · {" "}
                                        {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter((entry) => entry.status === "deleted").length} deleted
                                      </span>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>Search</span>
                                        <input
                                          onChange={(event) => {
                                            setProviderProvenanceSchedulerStitchedReportGovernanceCatalogSearch(
                                              event.target.value,
                                            );
                                          }}
                                          placeholder="catalog, guidance, policy"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch}
                                        />
                                      </label>
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Catalog</th>
                                            <th>Defaults</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((catalog) => (
                                            <tr key={`provider-scheduler-stitched-governance-catalog-${catalog.catalog_id}`}>
                                              <td>
                                                <strong>{catalog.name}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.status)} · {catalog.policy_template_ids.length} linked template(s)
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  Scope {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.description || "No stitched report catalog description recorded."}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>
                                                  {catalog.default_policy_template_name ?? "No default policy template"}
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.hierarchy_steps.length} hierarchy step(s)
                                                </p>
                                                {catalog.guidance ? (
                                                  <p className="run-lineage-symbol-copy">{catalog.guidance}</p>
                                                ) : null}
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    disabled={catalog.status !== "active"}
                                                    onClick={() => {
                                                      applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Use defaults
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
                                                    onClick={() => {
                                                      applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
                                                      void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Stage queue
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Open shared catalog
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : (
                                      <p className="empty-state">No stitched report policy catalogs match the current search.</p>
                                    )}
                                  </div>
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Stitched governance registry approval queue</strong>
                                      <p>
                                        Review staged governance plans for stitched-report governance registries
                                        without leaving the registry lifecycle workspace. This keeps queue-slice bundle
                                        approvals and rollback state next to the registry objects they mutate.
                                      </p>
                                    </div>
                                    <div className="provider-provenance-governance-summary">
                                      <strong>
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.total} registry plan(s)
                                      </strong>
                                      <span>
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.pending_approval_count} pending approval · {" "}
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.ready_to_apply_count} ready to apply · {" "}
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.completed_count} completed
                                      </span>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>Queue state</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              queue_state:
                                                event.target.value === "pending_approval"
                                                || event.target.value === "ready_to_apply"
                                                || event.target.value === "completed"
                                                  ? event.target.value
                                                  : ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.queue_state}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All states</option>
                                          <option value="pending_approval">Pending approval</option>
                                          <option value="ready_to_apply">Ready to apply</option>
                                          <option value="completed">Completed</option>
                                        </select>
                                      </label>
                                      <label>
                                        <span>Lane</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              approval_lane: event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.approval_lane}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All lanes</option>
                                          {Array.from(
                                            new Set(
                                              providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.map(
                                                (entry) => entry.approval_lane,
                                              ),
                                            ),
                                          ).sort().map((lane) => (
                                            <option key={lane} value={lane}>
                                              {formatWorkflowToken(lane)}
                                            </option>
                                          ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Priority</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              approval_priority: event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.approval_priority}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All priorities</option>
                                          <option value="low">Low</option>
                                          <option value="normal">Normal</option>
                                          <option value="high">High</option>
                                          <option value="critical">Critical</option>
                                        </select>
                                      </label>
                                      <label>
                                        <span>Policy template</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              policy_template_id:
                                                event.target.value === ""
                                                  ? ""
                                                  : event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.policy_template_id}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All policy templates</option>
                                          <option value="">No policy template</option>
                                          {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                                              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Policy catalog</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              policy_catalog_id:
                                                event.target.value === ""
                                                  ? ""
                                                  : event.target.value || ALL_FILTER_VALUE,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.policy_catalog_id}
                                        >
                                          <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
                                          <option value="">No policy catalog</option>
                                          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.map((entry) => (
                                            <option key={entry.catalog_id} value={entry.catalog_id}>
                                              {entry.name}
                                            </option>
                                          ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Search</span>
                                        <input
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              search: event.target.value,
                                            }))
                                          }
                                          placeholder="plan, registry, policy"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.search}
                                        />
                                      </label>
                                      <label>
                                        <span>Sort</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                                              ...current,
                                              sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                                                event.target.value,
                                              ),
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.sort}
                                        >
                                          <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
                                            Queue priority
                                          </option>
                                          <option value="updated_desc">Updated newest</option>
                                          <option value="updated_asc">Updated oldest</option>
                                          <option value="created_desc">Created newest</option>
                                          <option value="created_asc">Created oldest</option>
                                        </select>
                                      </label>
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading ? (
                                      <p className="empty-state">Loading stitched governance registry approval queue…</p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError ? (
                                      <p className="market-data-workflow-feedback">
                                        Stitched governance registry approval queue failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError}
                                      </p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Plan</th>
                                            <th>Preview</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.map((plan) => (
                                            <tr key={`provider-scheduler-stitched-governance-registry-plan-${plan.plan_id}`}>
                                              <td>
                                                <strong>
                                                  {formatWorkflowToken(plan.action)} stitched_report_governance_registry
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}
                                                  {plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}
                                                  {plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
                                                </p>
                                                {plan.policy_guidance ? (
                                                  <p className="run-lineage-symbol-copy">{plan.policy_guidance}</p>
                                                ) : null}
                                              </td>
                                              <td>
                                                <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
                                                <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
                                                <p className="run-lineage-symbol-copy">
                                                  {plan.preview_items.length} preview row(s) · rollback ready {plan.rollback_ready_count}
                                                </p>
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      reviewProviderProvenanceSchedulerStitchedReportGovernanceRegistryPlanInSharedQueue(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
                                                      ? "Shared queue selected"
                                                      : "Review in shared queue"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={
                                                      plan.status !== "previewed"
                                                      || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                                    }
                                                    onClick={() => {
                                                      void approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
                                                      ? "Approving…"
                                                      : "Approve"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={
                                                      plan.status !== "approved"
                                                      || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                                    }
                                                    onClick={() => {
                                                      void applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
                                                      ? "Applying…"
                                                      : "Apply"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={
                                                      plan.status !== "applied"
                                                      || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                                    }
                                                    onClick={() => {
                                                      void rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                                                    }}
                                                    type="button"
                                                  >
                                                    {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
                                                      ? "Rolling back…"
                                                      : "Rollback"}
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : (
                                      !providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading
                                        ? <p className="empty-state">No stitched governance registry plans match the dedicated queue filters.</p>
                                        : null
                                    )}
                                  </div>
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Stitched governance registry policy catalogs</strong>
                                      <p>
                                        Review only governance catalogs that can drive stitched-governance-registry
                                        approvals, then apply those defaults or jump into the shared catalog workspace
                                        when deeper hierarchy maintenance is needed.
                                      </p>
                                    </div>
                                    <div className="provider-provenance-governance-summary">
                                      <strong>
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length} registry catalog(s)
                                      </strong>
                                      <span>
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "active").length} active · {" "}
                                        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "deleted").length} deleted
                                      </span>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>Search</span>
                                        <input
                                          onChange={(event) => {
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch(
                                              event.target.value,
                                            );
                                          }}
                                          placeholder="catalog, guidance, registry policy"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch}
                                        />
                                      </label>
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Catalog</th>
                                            <th>Defaults</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.map((catalog) => (
                                            <tr key={`provider-scheduler-stitched-governance-registry-catalog-${catalog.catalog_id}`}>
                                              <td>
                                                <strong>{catalog.name}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.status)} · {catalog.policy_template_ids.length} linked template(s)
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  Scope {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.description || "No stitched governance registry catalog description recorded."}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>
                                                  {catalog.default_policy_template_name ?? "No default policy template"}
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.hierarchy_steps.length} hierarchy step(s)
                                                </p>
                                                {catalog.guidance ? (
                                                  <p className="run-lineage-symbol-copy">{catalog.guidance}</p>
                                                ) : null}
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    disabled={catalog.status !== "active"}
                                                    onClick={() => {
                                                      applyProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalog(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Use defaults
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Open shared catalog
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : (
                                      <p className="empty-state">No stitched governance registry policy catalogs match the current search.</p>
                                    )}
                                  </div>
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Stitched report governance registries</strong>
                                      <p>
                                        Save the stitched-report-only approval queue slice and default policy layer as
                                        a dedicated lifecycle object, then reapply or restore it without reopening the
                                        shared governance workspace.
                                      </p>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>Name</span>
                                        <input
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                                              ...current,
                                              name: event.target.value,
                                            }))
                                          }
                                          placeholder="Lag stitched governance"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.name}
                                        />
                                      </label>
                                      <label>
                                        <span>Description</span>
                                        <input
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                                              ...current,
                                              description: event.target.value,
                                            }))
                                          }
                                          placeholder="Queue slice and default policy bundle"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.description}
                                        />
                                      </label>
                                      <label>
                                        <span>Default policy template</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                                              ...current,
                                              default_policy_template_id: event.target.value,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.default_policy_template_id}
                                        >
                                          <option value="">No default policy template</option>
                                          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                                            .filter((entry) =>
                                              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                                                entry.item_type_scope,
                                                "stitched_report_view",
                                              ),
                                            )
                                            .map((entry) => (
                                              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                        </select>
                                      </label>
                                      <label>
                                        <span>Default policy catalog</span>
                                        <select
                                          onChange={(event) =>
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                                              ...current,
                                              default_policy_catalog_id: event.target.value,
                                            }))
                                          }
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.default_policy_catalog_id}
                                        >
                                          <option value="">No default policy catalog</option>
                                          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
                                            <option key={entry.catalog_id} value={entry.catalog_id}>
                                              {entry.name}
                                            </option>
                                          ))}
                                        </select>
                                      </label>
                                      <div className="market-data-provenance-history-actions">
                                        <button
                                          className="ghost-button"
                                          onClick={() => {
                                            void saveCurrentProviderProvenanceSchedulerStitchedReportGovernanceRegistry();
                                          }}
                                          type="button"
                                        >
                                          {editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId
                                            ? "Update registry"
                                            : "Save registry"}
                                        </button>
                                        {editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId ? (
                                          <button
                                            className="ghost-button"
                                            onClick={() => {
                                              resetProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft();
                                            }}
                                            type="button"
                                          >
                                            Cancel edit
                                          </button>
                                        ) : null}
                                      </div>
                                    </div>
                                    <div className="filter-bar">
                                      <label>
                                        <span>Search</span>
                                        <input
                                          onChange={(event) => {
                                            setProviderProvenanceSchedulerStitchedReportGovernanceRegistrySearch(
                                              event.target.value,
                                            );
                                          }}
                                          placeholder="registry, queue, policy"
                                          type="text"
                                          value={providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch}
                                        />
                                      </label>
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
                                      <div className="provider-provenance-governance-bar">
                                        <div className="provider-provenance-governance-summary">
                                          <strong>
                                            {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length} selected
                                          </strong>
                                          <span>
                                            {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "active").length} active · {" "}
                                            {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "deleted").length} deleted
                                          </span>
                                        </div>
                                        <div className="market-data-provenance-history-actions">
                                          <label>
                                            <span>Policy</span>
                                            <select
                                              onChange={(event) => {
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId(
                                                  event.target.value,
                                                );
                                              }}
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId}
                                            >
                                              <option value="">No policy template</option>
                                              {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                                                  <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                    {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                                                  </option>
                                                ))}
                                            </select>
                                          </label>
                                          <button
                                            className="ghost-button"
                                            onClick={toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections}
                                            type="button"
                                          >
                                            {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                                              === providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
                                              ? "Clear all"
                                              : "Select all"}
                                          </button>
                                          <button
                                            className="ghost-button"
                                            disabled={
                                              !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                                              || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction !== null
                                            }
                                            onClick={() => {
                                              void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
                                                "delete",
                                              );
                                            }}
                                            type="button"
                                          >
                                            {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "delete"
                                              ? "Previewing…"
                                              : "Preview delete"}
                                          </button>
                                          <button
                                            className="ghost-button"
                                            disabled={
                                              !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                                              || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction !== null
                                            }
                                            onClick={() => {
                                              void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
                                                "restore",
                                              );
                                            }}
                                            type="button"
                                          >
                                            {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "restore"
                                              ? "Previewing…"
                                              : "Preview restore"}
                                          </button>
                                        </div>
                                      </div>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
                                      <div className="provider-provenance-governance-editor">
                                        <div className="market-data-provenance-history-head">
                                          <strong>Bulk stitched governance registry edits</strong>
                                          <p>
                                            Preview queue-slice, default-policy, and metadata changes as staged
                                            governance plans before approval and apply.
                                          </p>
                                        </div>
                                        <div className="filter-bar">
                                          <label>
                                            <span>Name prefix</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  name_prefix: event.target.value,
                                                }))
                                              }
                                              placeholder="Ops / "
                                              type="text"
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.name_prefix}
                                            />
                                          </label>
                                          <label>
                                            <span>Name suffix</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  name_suffix: event.target.value,
                                                }))
                                              }
                                              placeholder=" / reviewed"
                                              type="text"
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.name_suffix}
                                            />
                                          </label>
                                          <label>
                                            <span>Description append</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  description_append: event.target.value,
                                                }))
                                              }
                                              placeholder="shift-reviewed"
                                              type="text"
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.description_append}
                                            />
                                          </label>
                                          <label>
                                            <span>Queue state</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  queue_state: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.queue_state}
                                            >
                                              <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                              <option value={ALL_FILTER_VALUE}>All queue states</option>
                                              <option value="pending_approval">pending approval</option>
                                              <option value="ready_to_apply">ready to apply</option>
                                              <option value="completed">completed</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Lane</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  approval_lane: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.approval_lane}
                                            >
                                              <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                              <option value={ALL_FILTER_VALUE}>Clear lane</option>
                                              <option value="chatops">chatops</option>
                                              <option value="ops">ops</option>
                                              <option value="leadership">leadership</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Priority</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  approval_priority: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.approval_priority}
                                            >
                                              <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                              <option value={ALL_FILTER_VALUE}>Clear priority</option>
                                              <option value="low">low</option>
                                              <option value="normal">normal</option>
                                              <option value="high">high</option>
                                              <option value="critical">critical</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Search</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  search: event.target.value,
                                                }))
                                              }
                                              placeholder="keep current or blank to clear"
                                              type="text"
                                              value={
                                                providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.search
                                                === KEEP_CURRENT_BULK_GOVERNANCE_VALUE
                                                  ? ""
                                                  : providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.search
                                              }
                                            />
                                          </label>
                                          <label>
                                            <span>Sort</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  sort: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.sort}
                                            >
                                              <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                              <option value={ALL_FILTER_VALUE}>Clear sort</option>
                                              <option value="queue_priority">queue priority</option>
                                              <option value="updated_desc">updated newest</option>
                                              <option value="updated_asc">updated oldest</option>
                                              <option value="created_desc">created newest</option>
                                              <option value="created_asc">created oldest</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Default policy template</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  default_policy_template_id: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.default_policy_template_id}
                                            >
                                              <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                              <option value="">No default policy template</option>
                                              {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                                                  <option
                                                    key={entry.policy_template_id}
                                                    value={entry.policy_template_id}
                                                  >
                                                    {entry.name}
                                                  </option>
                                                ))}
                                            </select>
                                          </label>
                                          <label>
                                            <span>Default policy catalog</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                                                  ...current,
                                                  default_policy_catalog_id: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.default_policy_catalog_id}
                                            >
                                              <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                                              <option value="">No default policy catalog</option>
                                              {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
                                                <option key={entry.catalog_id} value={entry.catalog_id}>
                                                  {entry.name}
                                                </option>
                                              ))}
                                            </select>
                                          </label>
                                          <label>
                                            <span>Governance policy</span>
                                            <select
                                              onChange={(event) => {
                                                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId(
                                                  event.target.value,
                                                );
                                              }}
                                              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId}
                                            >
                                              <option value="">No policy template</option>
                                              {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                                                  <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                    {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                                                  </option>
                                                ))}
                                            </select>
                                          </label>
                                          <label>
                                            <span>Action</span>
                                            <div className="market-data-provenance-history-actions">
                                              <button
                                                className="ghost-button"
                                                disabled={
                                                  !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                                                  || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction
                                                  !== null
                                                }
                                                onClick={() => {
                                                  void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
                                                    "update",
                                                  );
                                                }}
                                                type="button"
                                              >
                                                {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "update"
                                                  ? "Previewing…"
                                                  : "Preview bulk edit"}
                                              </button>
                                            </div>
                                          </label>
                                        </div>
                                      </div>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading ? (
                                      <p className="empty-state">Loading stitched governance registries…</p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistriesError ? (
                                      <p className="market-data-workflow-feedback">
                                        Stitched governance registries failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistriesError}
                                      </p>
                                    ) : null}
                                    {filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>
                                              <input
                                                aria-label="Select all stitched governance registries"
                                                checked={
                                                  providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
                                                  > 0
                                                  && selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                                                  === providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
                                                }
                                                onChange={toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections}
                                                type="checkbox"
                                              />
                                            </th>
                                            <th>Registry</th>
                                            <th>Queue slice</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries.map((entry) => (
                                            <tr key={`provider-scheduler-stitched-governance-registry-${entry.registry_id}`}>
                                              <td className="provider-provenance-selection-cell">
                                                <input
                                                  aria-label={`Select stitched governance registry ${entry.name}`}
                                                  checked={selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet.has(entry.registry_id)}
                                                  onChange={() => {
                                                    toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelection(
                                                      entry.registry_id,
                                                    );
                                                  }}
                                                  type="checkbox"
                                                />
                                              </td>
                                              <td>
                                                <strong>{entry.name}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(entry.status)} · revisions {entry.revision_count}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.description || "No stitched governance registry description recorded."}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.default_policy_template_name ?? "No default policy template"}
                                                  {entry.default_policy_catalog_name
                                                    ? ` · ${entry.default_policy_catalog_name}`
                                                    : ""}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>
                                                  {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                                                    entry.queue_view,
                                                  ) ?? "All stitched governance plans"}
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  Saved {formatTimestamp(entry.updated_at)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                                                </p>
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      applyProviderProvenanceSchedulerStitchedReportGovernanceRegistry(entry);
                                                    }}
                                                    type="button"
                                                  >
                                                    Apply
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      editProviderProvenanceSchedulerStitchedReportGovernanceRegistry(entry);
                                                    }}
                                                    type="button"
                                                  >
                                                    Edit
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory(
                                                        entry.registry_id,
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryId === entry.registry_id
                                                      && selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory
                                                      ? "Hide versions"
                                                      : "Versions"}
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={entry.status !== "active"}
                                                    onClick={() => {
                                                      void deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry(
                                                        entry,
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    Delete
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : (
                                      !providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading
                                        ? <p className="empty-state">No stitched governance registries match the current search.</p>
                                        : null
                                    )}
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Stitched governance registry team audit</strong>
                                        <p>
                                          Review registry lifecycle and bulk governance changes by registry, actor, or
                                          reason without leaving the stitched-report governance surface.
                                        </p>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Registry</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                                                ...current,
                                                registry_id: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.registry_id}
                                          >
                                            <option value="">All registries</option>
                                            {providerProvenanceSchedulerStitchedReportGovernanceRegistries.map((entry) => (
                                              <option key={entry.registry_id} value={entry.registry_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                                                ...current,
                                                action: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.action}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All actions</option>
                                            <option value="created">Created</option>
                                            <option value="updated">Updated</option>
                                            <option value="deleted">Deleted</option>
                                            <option value="restored">Restored</option>
                                          </select>
                                        </label>
                                        <label>
                                          <span>Actor tab</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                                                ...current,
                                                actor_tab_id: event.target.value,
                                              }))
                                            }
                                            placeholder="tab_ops"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.actor_tab_id}
                                          />
                                        </label>
                                        <label>
                                          <span>Search</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                                                ...current,
                                                search: event.target.value,
                                              }))
                                            }
                                            placeholder="lag reviewed"
                                            type="text"
                                            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.search}
                                          />
                                        </label>
                                      </div>
                                      {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading ? (
                                        <p className="empty-state">Loading stitched governance registry audit…</p>
                                      ) : null}
                                      {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError ? (
                                        <p className="market-data-workflow-feedback">
                                          Stitched governance registry audit failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError}
                                        </p>
                                      ) : null}
                                      {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>When</th>
                                              <th>Action</th>
                                              <th>Actor</th>
                                              <th>Detail</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.map((entry) => (
                                              <tr key={`provider-scheduler-stitched-governance-registry-audit-${entry.audit_id}`}>
                                                <td>
                                                  <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                  <p className="run-lineage-symbol-copy">{entry.name}</p>
                                                </td>
                                                <td>
                                                  <strong>{formatWorkflowToken(entry.action)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.status)} · {" "}
                                                    {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                                                      entry.queue_view,
                                                    ) ?? "All stitched governance plans"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.actor_tab_id ?? "No tab id recorded."}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{entry.detail}</strong>
                                                  <p className="run-lineage-symbol-copy">{entry.reason}</p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.default_policy_template_name ?? "No default policy template"}
                                                    {entry.default_policy_catalog_name
                                                      ? ` · ${entry.default_policy_catalog_name}`
                                                      : ""}
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        !providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading
                                          ? <p className="empty-state">No stitched governance registry audit events match the selected filters.</p>
                                          : null
                                      )}
                                    </div>
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryLoading ? (
                                      <p className="empty-state">Loading stitched governance registry history…</p>
                                    ) : null}
                                    {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError ? (
                                      <p className="market-data-workflow-feedback">
                                        Registry history failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError}
                                      </p>
                                    ) : null}
                                    {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Recorded</th>
                                            <th>Snapshot</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory.history.map((entry) => (
                                            <tr key={`provider-scheduler-stitched-governance-registry-revision-${entry.revision_id}`}>
                                              <td>
                                                <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>{entry.name}</strong>
                                                <p className="run-lineage-symbol-copy">{entry.description || "No description recorded."}</p>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                                                    entry.queue_view,
                                                  ) ?? "All stitched governance plans"}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.default_policy_template_name ?? "No default policy template"}
                                                  {entry.default_policy_catalog_name
                                                    ? ` · ${entry.default_policy_catalog_name}`
                                                    : ""}
                                                </p>
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      applyProviderProvenanceSchedulerStitchedReportGovernanceRegistry(
                                                        {
                                                          ...selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory.registry,
                                                          name: entry.name,
                                                          description: entry.description,
                                                          queue_view: entry.queue_view,
                                                          default_policy_template_id: entry.default_policy_template_id,
                                                          default_policy_template_name: entry.default_policy_template_name,
                                                          default_policy_catalog_id: entry.default_policy_catalog_id,
                                                          default_policy_catalog_name: entry.default_policy_catalog_name,
                                                        },
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    Apply snapshot
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistoryRevision(
                                                        entry,
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    Restore revision
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : null}
                                  </div>
                                  <div className="market-data-provenance-history-head">
                                    <strong>Shared scheduler exports</strong>
                                    <p>
                                      {providerProvenanceSchedulerExports.length
                                        ? `${providerProvenanceSchedulerExports.length} server-side scheduler export snapshot(s) are available.`
                                        : "No shared scheduler exports have been recorded yet."}
                                    </p>
                                  </div>
                                  {providerProvenanceSchedulerExportsLoading ? (
                                    <p className="empty-state">Loading shared scheduler export registry…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerExportsError ? (
                                    <p className="market-data-workflow-feedback">
                                      Shared scheduler export registry failed: {providerProvenanceSchedulerExportsError}
                                    </p>
                                  ) : null}
                                  {providerProvenanceSchedulerExports.length ? (
                                    <table className="data-table">
                                      <thead>
                                        <tr>
                                          <th>Exported</th>
                                          <th>Status</th>
                                          <th>Delivery</th>
                                          <th>Action</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {providerProvenanceSchedulerExports.map((entry) => (
                                          <tr key={`provider-scheduler-export-${entry.job_id}`}>
                                            <td>
                                              <strong>{formatTimestamp(entry.exported_at ?? entry.created_at)}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.filter_summary ?? "No scheduler export filter summary recorded."}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                Requested by {entry.requested_by_tab_label ?? entry.requested_by_tab_id ?? "unknown tab"}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{entry.result_count} cycle record(s)</strong>
                                              <p className="run-lineage-symbol-copy">
                                                Scope {formatWorkflowToken(entry.export_scope)}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                Route {formatWorkflowToken(entry.routing_policy_id ?? "default")} · {entry.routing_targets.length
                                                  ? entry.routing_targets.join(", ")
                                                  : "no targets"}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                Escalations {entry.escalation_count}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{formatWorkflowToken(entry.last_delivery_status ?? "not_escalated")}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.last_delivery_summary ?? "Not escalated yet."}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                Approval {formatWorkflowToken(entry.approval_state)} · {entry.approval_summary ?? "No approval summary recorded."}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.last_escalated_at
                                                  ? `Last escalated ${formatTimestamp(entry.last_escalated_at)} by ${entry.last_escalated_by ?? "operator"}`
                                                  : "No escalation recorded."}
                                              </p>
                                            </td>
                                            <td>
                                              <div className="market-data-provenance-history-actions">
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void copySharedProviderProvenanceSchedulerExport(entry);
                                                  }}
                                                  type="button"
                                                >
                                                  Copy export
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void loadProviderProvenanceSchedulerExportHistory(entry.job_id);
                                                  }}
                                                  type="button"
                                                >
                                                  View history
                                                </button>
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    void escalateSharedProviderProvenanceSchedulerExport(entry);
                                                  }}
                                                  disabled={entry.approval_required && entry.approval_state !== "approved"}
                                                  type="button"
                                                >
                                                  Escalate
                                                </button>
                                              </div>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  ) : null}
                                  {selectedProviderProvenanceSchedulerExportJobId ? (
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Scheduler export audit trail</strong>
                                        <p>{shortenIdentifier(selectedProviderProvenanceSchedulerExportJobId, 10)}</p>
                                      </div>
                                      {selectedProviderProvenanceSchedulerExportEntry ? (
                                        <div className="provider-provenance-workspace-card">
                                          <div className="market-data-provenance-history-head">
                                            <strong>Escalation policy</strong>
                                            <p>
                                              Save a per-export routing policy, require approval when needed, and then
                                              escalate the selected scheduler snapshot.
                                            </p>
                                          </div>
                                          <div className="filter-bar">
                                            <label>
                                              <span>Route</span>
                                              <select
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                                                    ...current,
                                                    routing_policy_id: event.target.value,
                                                    delivery_targets:
                                                      event.target.value === "custom"
                                                        ? (
                                                          current.delivery_targets.length
                                                            ? current.delivery_targets
                                                            : [...selectedProviderProvenanceSchedulerExportEntry.available_delivery_targets]
                                                        )
                                                        : current.delivery_targets,
                                                  }))
                                                }
                                                value={providerProvenanceSchedulerExportPolicyDraft.routing_policy_id}
                                              >
                                                <option value="default">Default recommendation</option>
                                                <option value="chatops_only">Chatops only</option>
                                                <option value="all_targets">All targets</option>
                                                <option value="paging_only">Paging only</option>
                                                <option value="custom">Custom targets</option>
                                              </select>
                                            </label>
                                            <label>
                                              <span>Approval</span>
                                              <select
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                                                    ...current,
                                                    approval_policy_id: event.target.value === "manual_required"
                                                      ? "manual_required"
                                                      : "auto",
                                                  }))
                                                }
                                                value={providerProvenanceSchedulerExportPolicyDraft.approval_policy_id}
                                              >
                                                <option value="auto">Auto</option>
                                                <option value="manual_required">Manual approval required</option>
                                              </select>
                                            </label>
                                            <label>
                                              <span>Approval note</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                                                    ...current,
                                                    approval_note: event.target.value,
                                                  }))
                                                }
                                                placeholder="manager_review_complete"
                                                type="text"
                                                value={providerProvenanceSchedulerExportPolicyDraft.approval_note}
                                              />
                                            </label>
                                          </div>
                                          {providerProvenanceSchedulerExportPolicyDraft.routing_policy_id === "custom" ? (
                                            <div className="filter-bar">
                                              {selectedProviderProvenanceSchedulerExportEntry.available_delivery_targets.map((target) => (
                                                <label className="provider-provenance-checkbox" key={`provider-scheduler-target-${target}`}>
                                                  <input
                                                    checked={providerProvenanceSchedulerExportPolicyDraft.delivery_targets.includes(target)}
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                                                        ...current,
                                                        delivery_targets: event.target.checked
                                                          ? Array.from(new Set([...current.delivery_targets, target]))
                                                          : current.delivery_targets.filter((candidate) => candidate !== target),
                                                      }))
                                                    }
                                                    type="checkbox"
                                                  />
                                                  <span>{target}</span>
                                                </label>
                                              ))}
                                            </div>
                                          ) : null}
                                          <div className="run-filter-summary-chip-row">
                                            <span className="run-filter-summary-chip">
                                              Current route {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.routing_policy_id ?? "default")}
                                            </span>
                                            <span className="run-filter-summary-chip">
                                              Targets {selectedProviderProvenanceSchedulerExportEntry.routing_targets.length
                                                ? selectedProviderProvenanceSchedulerExportEntry.routing_targets.join(", ")
                                                : "none"}
                                            </span>
                                            <span className="run-filter-summary-chip">
                                              Approval {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.approval_state)}
                                            </span>
                                            {selectedProviderProvenanceSchedulerExportEntry.approved_at ? (
                                              <span className="run-filter-summary-chip">
                                                Approved {formatTimestamp(selectedProviderProvenanceSchedulerExportEntry.approved_at)} by {selectedProviderProvenanceSchedulerExportEntry.approved_by ?? "unknown"}
                                              </span>
                                            ) : null}
                                          </div>
                                          <p className="market-data-workflow-export-copy">
                                            {selectedProviderProvenanceSchedulerExportEntry.routing_policy_summary ?? "No routing summary recorded."}{" "}
                                            {selectedProviderProvenanceSchedulerExportEntry.approval_summary ?? "No approval summary recorded."}
                                          </p>
                                          <div className="market-data-provenance-history-actions">
                                            <button
                                              className="ghost-button"
                                              onClick={() => {
                                                void updateSharedProviderProvenanceSchedulerExportPolicy(
                                                  selectedProviderProvenanceSchedulerExportEntry,
                                                );
                                              }}
                                              type="button"
                                            >
                                              Save policy
                                            </button>
                                            <button
                                              className="ghost-button"
                                              disabled={
                                                !selectedProviderProvenanceSchedulerExportEntry.approval_required
                                                || selectedProviderProvenanceSchedulerExportEntry.approval_state === "approved"
                                              }
                                              onClick={() => {
                                                void approveSharedProviderProvenanceSchedulerExport(
                                                  selectedProviderProvenanceSchedulerExportEntry,
                                                );
                                              }}
                                              type="button"
                                            >
                                              Approve route
                                            </button>
                                            <button
                                              className="ghost-button"
                                              disabled={
                                                selectedProviderProvenanceSchedulerExportEntry.approval_required
                                                && selectedProviderProvenanceSchedulerExportEntry.approval_state !== "approved"
                                              }
                                              onClick={() => {
                                                void escalateSharedProviderProvenanceSchedulerExport(
                                                  selectedProviderProvenanceSchedulerExportEntry,
                                                );
                                              }}
                                              type="button"
                                            >
                                              Escalate now
                                            </button>
                                          </div>
                                        </div>
                                      ) : null}
                                      {providerProvenanceSchedulerExportHistoryLoading ? (
                                        <p className="empty-state">Loading scheduler export audit trail…</p>
                                      ) : null}
                                      {providerProvenanceSchedulerExportHistoryError ? (
                                        <p className="market-data-workflow-feedback">
                                          Scheduler export audit failed: {providerProvenanceSchedulerExportHistoryError}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceSchedulerExportHistory?.history.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>When</th>
                                              <th>Action</th>
                                              <th>Actor</th>
                                              <th>Detail</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {selectedProviderProvenanceSchedulerExportHistory.history.map((record) => (
                                              <tr key={`provider-scheduler-export-audit-${record.audit_id}`}>
                                                <td>{formatTimestamp(record.recorded_at)}</td>
                                                <td>
                                                  <strong>{formatWorkflowToken(record.action)}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {record.delivery_status
                                                      ? formatWorkflowToken(record.delivery_status)
                                                      : "No delivery state recorded."}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{record.source_tab_label ?? record.requested_by_tab_label ?? "unknown tab"}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {record.source_tab_id ?? record.requested_by_tab_id ?? "No tab id recorded."}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{record.detail}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Route {formatWorkflowToken(record.routing_policy_id ?? "default")} · {record.routing_targets.length
                                                      ? record.routing_targets.join(", ")
                                                      : "no routing targets recorded"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    Approval {record.approval_state
                                                      ? formatWorkflowToken(record.approval_state)
                                                      : "not recorded"} · {record.approval_summary ?? "No approval summary recorded."}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {record.delivery_targets.length
                                                      ? `Targets: ${record.delivery_targets.join(", ")}`
                                                      : "No delivery targets recorded."}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {record.delivery_summary ?? "No delivery summary recorded."}
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : selectedProviderProvenanceSchedulerExportHistory && !providerProvenanceSchedulerExportHistoryLoading ? (
                                        <p className="empty-state">No scheduler export audit events recorded yet.</p>
                                      ) : null}
                                    </div>
                                  ) : null}
                                </div>
                              ) : null}
                              {providerProvenanceAnalyticsLoading ? (
                                <p className="empty-state">Loading provider provenance analytics…</p>
                              ) : null}
                              {providerProvenanceAnalyticsError ? (
                                <p className="market-data-workflow-feedback">
                                  Provider provenance analytics failed: {providerProvenanceAnalyticsError}
                                </p>
                              ) : null}
                              {providerProvenanceAnalytics ? (
                                <>
                                  <div className="status-grid">
                                    <div className="metric-tile">
                                      <span>Matched exports</span>
                                      <strong>{providerProvenanceAnalytics.totals.export_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Result count</span>
                                      <strong>{providerProvenanceAnalytics.totals.result_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Provenance incidents</span>
                                      <strong>{providerProvenanceAnalytics.totals.provider_provenance_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Download audits</span>
                                      <strong>{providerProvenanceAnalytics.totals.download_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Providers</span>
                                      <strong>{providerProvenanceAnalytics.totals.provider_label_count}</strong>
                                    </div>
                                    <div className="metric-tile">
                                      <span>Vendor fields</span>
                                      <strong>{providerProvenanceAnalytics.totals.vendor_field_count}</strong>
                                    </div>
                                  </div>
                                  {providerProvenanceDashboardLayout.show_time_series ? (
                                    <div className="status-grid-two-column market-data-provenance-time-series-grid">
                                      <div className="market-data-provenance-time-series-panel">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Provider drift by day</strong>
                                        <p>
                                          Daily provider-native market-context incidents for the current analytics
                                          query window.
                                        </p>
                                      </div>
                                      <div className="run-filter-summary-chip-row">
                                        <span className="run-filter-summary-chip">
                                          Peak {providerProvenanceAnalytics.time_series.provider_drift.summary.peak_bucket_label ?? "n/a"} · {" "}
                                          {providerProvenanceAnalytics.time_series.provider_drift.summary.peak_provider_provenance_count} incident(s)
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          Latest {providerProvenanceAnalytics.time_series.provider_drift.summary.latest_bucket_label ?? "n/a"} · {" "}
                                          {providerProvenanceAnalytics.time_series.provider_drift.summary.latest_provider_provenance_count} incident(s)
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          {providerProvenanceAnalytics.time_series.window_days} daily bucket(s)
                                        </span>
                                      </div>
                                      {providerProvenanceAnalytics.time_series.provider_drift.series.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Day</th>
                                              <th>Drift</th>
                                              <th>Coverage</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceAnalytics.time_series.provider_drift.series.map((bucket) => (
                                              <tr key={`provider-drift-bucket-${bucket.bucket_key}`}>
                                                <td>
                                                  <strong>{bucket.bucket_label}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {bucket.bucket_key}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{bucket.provider_provenance_count} incident(s)</strong>
                                                  <div className="market-data-provenance-timeseries-track">
                                                    <div
                                                      className="market-data-provenance-timeseries-bar"
                                                      style={{
                                                        width: resolveProviderProvenanceSeriesBarWidth(
                                                          bucket.provider_provenance_count,
                                                          providerProvenanceDriftBarMax,
                                                        ),
                                                      }}
                                                    />
                                                  </div>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatProviderDriftIntensity(bucket.drift_intensity)}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{bucket.export_count} export(s)</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {bucket.focus_count} focus anchor(s) · {bucket.provider_label_count} provider(s)
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {bucket.provider_labels.length ? bucket.provider_labels.join(", ") : "No provider mix recorded."}
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No provider drift buckets match the current query.</p>
                                      )}
                                      </div>
                                      <div className="market-data-provenance-time-series-panel">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Export burn-up</strong>
                                        <p>
                                          Daily export delta plus cumulative exports, downloads, and provider
                                          provenance incidents.
                                        </p>
                                      </div>
                                      <div className="run-filter-summary-chip-row">
                                        <span className="run-filter-summary-chip">
                                          {providerProvenanceAnalytics.time_series.export_burn_up.summary.cumulative_export_count} cumulative export(s)
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          {providerProvenanceAnalytics.time_series.export_burn_up.summary.cumulative_download_count} cumulative download(s)
                                        </span>
                                        <span className="run-filter-summary-chip">
                                          {providerProvenanceAnalytics.time_series.export_burn_up.summary.cumulative_provider_provenance_count} cumulative incident(s)
                                        </span>
                                      </div>
                                      {providerProvenanceAnalytics.time_series.export_burn_up.series.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Day</th>
                                              <th>Delta</th>
                                              <th>Cumulative</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceAnalytics.time_series.export_burn_up.series.map((bucket) => (
                                              <tr key={`provider-burn-up-bucket-${bucket.bucket_key}`}>
                                                <td>
                                                  <strong>{bucket.bucket_label}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {bucket.bucket_key}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>+{bucket.export_count} export(s)</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    +{bucket.download_count} download(s) · +{bucket.provider_provenance_count} incident(s)
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    +{bucket.result_count} result(s)
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{bucket.cumulative_export_count} export(s)</strong>
                                                  <div className="market-data-provenance-timeseries-track">
                                                    <div
                                                      className="market-data-provenance-timeseries-bar is-burn-up"
                                                      style={{
                                                        width: resolveProviderProvenanceSeriesBarWidth(
                                                          bucket.cumulative_export_count,
                                                          providerProvenanceBurnUpBarMax,
                                                        ),
                                                      }}
                                                    />
                                                  </div>
                                                  <p className="run-lineage-symbol-copy">
                                                    {bucket.cumulative_download_count} downloads · {bucket.cumulative_provider_provenance_count} incidents
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No burn-up buckets match the current query.</p>
                                      )}
                                      </div>
                                    </div>
                                  ) : null}
                                  {providerProvenanceDashboardLayout.show_rollups ? (
                                    <div className="status-grid-two-column">
                                      <div>
                                      <h3>Provider rollup</h3>
                                      {providerProvenanceAnalytics.rollups.providers.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Provider</th>
                                              <th>Exports</th>
                                              <th>Signal</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceAnalytics.rollups.providers.map((rollup) => (
                                              <tr key={`provider-rollup-${rollup.key}`}>
                                                <td>
                                                  <strong>{rollup.label}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.focus_count} focus anchor(s)
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{rollup.export_count}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.provider_provenance_count} provenance incidents
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{rollup.download_count} downloads</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Last export: {formatTimestamp(rollup.last_exported_at)}
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No provider rollups match the current query.</p>
                                      )}
                                      </div>
                                      <div>
                                      <h3>Focus hotspots</h3>
                                      {providerProvenanceAnalytics.rollups.focuses.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Focus</th>
                                              <th>Exports</th>
                                              <th>Action</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceAnalytics.rollups.focuses.map((rollup) => (
                                              <tr key={`focus-rollup-${rollup.key}`}>
                                                <td>
                                                  <strong>{rollup.label}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.market_data_provider ?? "n/a"} / {rollup.venue ?? "n/a"} / {rollup.symbol ?? "n/a"} · {rollup.timeframe ?? "n/a"}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{rollup.export_count}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.download_count} downloads
                                                  </p>
                                                </td>
                                                <td>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void focusMarketInstrumentFromProviderExport({
                                                        focus_key: rollup.key,
                                                        focus_label: rollup.label,
                                                      });
                                                    }}
                                                    type="button"
                                                  >
                                                    Focus triage
                                                  </button>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No focus hotspots match the current query.</p>
                                      )}
                                      </div>
                                    </div>
                                  ) : null}
                                  {providerProvenanceDashboardLayout.show_rollups ? (
                                    <div className="status-grid-two-column">
                                      <div>
                                      <h3>Vendor-field rollup</h3>
                                      {providerProvenanceAnalytics.rollups.vendor_fields.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Vendor field</th>
                                              <th>Exports</th>
                                              <th>Signal</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceAnalytics.rollups.vendor_fields.map((rollup) => (
                                              <tr key={`vendor-rollup-${rollup.key}`}>
                                                <td><strong>{rollup.label}</strong></td>
                                                <td>
                                                  <strong>{rollup.export_count}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.provider_provenance_count} provenance incidents
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{rollup.focus_count} focus anchor(s)</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.download_count} downloads
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No vendor-field rollups match the current query.</p>
                                      )}
                                      </div>
                                      <div>
                                      <h3>Requester rollup</h3>
                                      {providerProvenanceAnalytics.rollups.requesters.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Requester</th>
                                              <th>Exports</th>
                                              <th>Signal</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceAnalytics.rollups.requesters.map((rollup) => (
                                              <tr key={`requester-rollup-${rollup.key}`}>
                                                <td><strong>{rollup.label}</strong></td>
                                                <td>
                                                  <strong>{rollup.export_count}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {rollup.focus_count} focus anchor(s)
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{rollup.download_count} downloads</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    Last export: {formatTimestamp(rollup.last_exported_at)}
                                                  </p>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No requester rollups match the current query.</p>
                                      )}
                                      </div>
                                    </div>
                                  ) : null}
                                  {providerProvenanceDashboardLayout.show_recent_exports ? (
                                    <div>
                                    <h3>Cross-focus results</h3>
                                    {providerProvenanceAnalytics.recent_exports.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Exported</th>
                                            <th>Focus</th>
                                            <th>Providers</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceAnalytics.recent_exports.map((entry) => (
                                            <tr key={`cross-focus-${entry.job_id}`}>
                                              <td>{formatTimestamp(entry.exported_at ?? entry.created_at)}</td>
                                              <td>
                                                <strong>{entry.focus_label ?? "Unknown focus"}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.market_data_provider ?? "n/a"} / {entry.symbol ?? "n/a"} · {entry.timeframe ?? "n/a"}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>{entry.provider_labels.join(", ") || "n/a"}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {entry.vendor_fields.join(", ") || "n/a"}
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
                                                    Copy export
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void focusMarketInstrumentFromProviderExport(entry);
                                                    }}
                                                    type="button"
                                                  >
                                                    Focus triage
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void loadSharedProviderProvenanceExportHistory(entry.job_id);
                                                    }}
                                                    type="button"
                                                  >
                                                    View history
                                                  </button>
                                                </div>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    ) : (
                                      <p className="empty-state">No shared provider provenance exports match the current analytics query.</p>
                                    )}
                                    </div>
                                  ) : null}
                                </>
                              ) : null}
                            </div>
                            {selectedSharedProviderProvenanceExportJobId ? (
                              <div className="market-data-provenance-shared-history">
                                <div className="market-data-provenance-history-head">
                                  <strong>Shared registry audit trail</strong>
                                  <p>
                                    {selectedSharedProviderProvenanceExportHistory?.job.focus_label
                                      ? `${selectedSharedProviderProvenanceExportHistory.job.focus_label} · ${shortenIdentifier(selectedSharedProviderProvenanceExportJobId, 10)}`
                                      : shortenIdentifier(selectedSharedProviderProvenanceExportJobId, 10)}
                                  </p>
                                </div>
                                {sharedProviderProvenanceExportHistoryLoading ? (
                                  <p className="empty-state">Loading shared export audit trail…</p>
                                ) : null}
                                {sharedProviderProvenanceExportHistoryError ? (
                                  <p className="market-data-workflow-feedback">
                                    Shared export audit load failed: {sharedProviderProvenanceExportHistoryError}
                                  </p>
                                ) : null}
                                {selectedSharedProviderProvenanceExportHistory?.history.length ? (
                                  <table className="data-table">
                                    <thead>
                                      <tr>
                                        <th>When</th>
                                        <th>Action</th>
                                        <th>Actor</th>
                                        <th>Detail</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {selectedSharedProviderProvenanceExportHistory.history.map((record) => (
                                        <tr key={record.audit_id}>
                                          <td>{formatTimestamp(record.recorded_at)}</td>
                                          <td>{formatWorkflowToken(record.action)}</td>
                                          <td>
                                            <strong>{record.source_tab_label ?? record.requested_by_tab_label ?? "unknown tab"}</strong>
                                            <p className="run-lineage-symbol-copy">
                                              {record.source_tab_id ?? record.requested_by_tab_id ?? "No tab id recorded."}
                                            </p>
                                          </td>
                                          <td>
                                            <strong>{record.detail}</strong>
                                            <p className="run-lineage-symbol-copy">
                                              {record.market_data_provider ?? "n/a"} / {record.symbol ?? "n/a"} · {record.timeframe ?? "n/a"}
                                            </p>
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                ) : selectedSharedProviderProvenanceExportHistory && !sharedProviderProvenanceExportHistoryLoading ? (
                                  <p className="empty-state">No shared export audit events recorded yet.</p>
                                ) : null}
                              </div>
                            ) : null}
                          </div>
                        </div>
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
