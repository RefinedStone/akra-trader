// @ts-nocheck
export function RuntimeProviderProvenanceFocusedReadbackSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
