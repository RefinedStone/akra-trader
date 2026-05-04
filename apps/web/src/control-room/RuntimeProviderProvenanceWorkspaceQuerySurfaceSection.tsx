// @ts-nocheck
export function RuntimeProviderProvenanceWorkspaceQuerySurfaceSection({
  model,
}: {
  model: any;
}) {
  const {
    setProviderProvenanceAnalyticsQuery,
    providerProvenanceAnalyticsQuery,
    ALL_FILTER_VALUE,
    providerProvenanceAnalytics,
    formatProviderProvenanceAnalyticsQuerySummary,
    providerProvenanceDashboardLayout,
  } = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Analytics and cross-focus query</strong>
        <p>
          Query the shared provider provenance registry across focuses and roll the results up into
          provider, vendor-field, and focus hotspots.
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
            {(providerProvenanceAnalytics?.available_filters.market_data_providers ?? []).map(
              (provider) => (
                <option key={provider} value={provider}>
                  {provider}
                </option>
              ),
            )}
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
            {(providerProvenanceAnalytics?.available_filters.requested_by_tab_ids ?? []).map(
              (requester) => (
                <option key={requester} value={requester}>
                  {requester}
                </option>
              ),
            )}
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
    </div>
  );
}
