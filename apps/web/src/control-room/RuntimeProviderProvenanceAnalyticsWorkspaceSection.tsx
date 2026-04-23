// @ts-nocheck
export function RuntimeProviderProvenanceAnalyticsWorkspaceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
