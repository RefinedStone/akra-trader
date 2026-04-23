// @ts-nocheck
export function RuntimeProviderProvenanceAnalyticsSummarySection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
