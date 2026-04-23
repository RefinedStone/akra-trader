// @ts-nocheck
export function RuntimeProviderProvenanceAnalyticsTimeSeriesSection({ model }: { model: any }) {
  const {} = model;

  if (!providerProvenanceDashboardLayout.show_time_series) {
    return null;
  }

  return (
    <div className="status-grid-two-column market-data-provenance-time-series-grid">
      <div className="market-data-provenance-time-series-panel">
        <div className="market-data-provenance-history-head">
          <strong>Provider drift by day</strong>
          <p>Daily provider-native market-context incidents for the current analytics query window.</p>
        </div>
        <div className="run-filter-summary-chip-row">
          <span className="run-filter-summary-chip">
            Peak {providerProvenanceAnalytics.time_series.provider_drift.summary.peak_bucket_label ?? "n/a"} ·{" "}
            {providerProvenanceAnalytics.time_series.provider_drift.summary
              .peak_provider_provenance_count}{" "}
            incident(s)
          </span>
          <span className="run-filter-summary-chip">
            Latest{" "}
            {providerProvenanceAnalytics.time_series.provider_drift.summary.latest_bucket_label ??
              "n/a"}{" "}
            ·{" "}
            {providerProvenanceAnalytics.time_series.provider_drift.summary
              .latest_provider_provenance_count}{" "}
            incident(s)
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
                    <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
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
                      {bucket.provider_labels.length
                        ? bucket.provider_labels.join(", ")
                        : "No provider mix recorded."}
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
            Daily export delta plus cumulative exports, downloads, and provider provenance
            incidents.
          </p>
        </div>
        <div className="run-filter-summary-chip-row">
          <span className="run-filter-summary-chip">
            {
              providerProvenanceAnalytics.time_series.export_burn_up.summary
                .cumulative_export_count
            }{" "}
            cumulative export(s)
          </span>
          <span className="run-filter-summary-chip">
            {
              providerProvenanceAnalytics.time_series.export_burn_up.summary
                .cumulative_download_count
            }{" "}
            cumulative download(s)
          </span>
          <span className="run-filter-summary-chip">
            {
              providerProvenanceAnalytics.time_series.export_burn_up.summary
                .cumulative_provider_provenance_count
            }{" "}
            cumulative incident(s)
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
                    <p className="run-lineage-symbol-copy">{bucket.bucket_key}</p>
                  </td>
                  <td>
                    <strong>+{bucket.export_count} export(s)</strong>
                    <p className="run-lineage-symbol-copy">
                      +{bucket.download_count} download(s) · +{bucket.provider_provenance_count} incident(s)
                    </p>
                    <p className="run-lineage-symbol-copy">+{bucket.result_count} result(s)</p>
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
                      {bucket.cumulative_download_count} downloads ·{" "}
                      {bucket.cumulative_provider_provenance_count} incidents
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
  );
}
