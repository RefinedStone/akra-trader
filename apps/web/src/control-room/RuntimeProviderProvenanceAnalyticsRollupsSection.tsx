// @ts-nocheck
export function RuntimeProviderProvenanceAnalyticsRollupsSection({ model }: { model: any }) {
  const {} = model;

  if (!providerProvenanceDashboardLayout.show_rollups) {
    return null;
  }

  return (
    <>
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
                      <p className="run-lineage-symbol-copy">{rollup.focus_count} focus anchor(s)</p>
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
                        {rollup.market_data_provider ?? "n/a"} / {rollup.venue ?? "n/a"} /{" "}
                        {rollup.symbol ?? "n/a"} · {rollup.timeframe ?? "n/a"}
                      </p>
                    </td>
                    <td>
                      <strong>{rollup.export_count}</strong>
                      <p className="run-lineage-symbol-copy">{rollup.download_count} downloads</p>
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
                    <td>
                      <strong>{rollup.label}</strong>
                    </td>
                    <td>
                      <strong>{rollup.export_count}</strong>
                      <p className="run-lineage-symbol-copy">
                        {rollup.provider_provenance_count} provenance incidents
                      </p>
                    </td>
                    <td>
                      <strong>{rollup.focus_count} focus anchor(s)</strong>
                      <p className="run-lineage-symbol-copy">{rollup.download_count} downloads</p>
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
                    <td>
                      <strong>{rollup.label}</strong>
                    </td>
                    <td>
                      <strong>{rollup.export_count}</strong>
                      <p className="run-lineage-symbol-copy">{rollup.focus_count} focus anchor(s)</p>
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
    </>
  );
}
