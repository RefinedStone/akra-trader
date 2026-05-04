// @ts-nocheck
export function RuntimeProviderProvenanceFocusedReadbackSection({ model }: { model: any }) {
  const {
    setMarketDataProvenanceExportFilter,
    marketDataProvenanceExportFilter,
    ALL_FILTER_VALUE,
    marketDataProvenanceExportProviderOptions,
    marketDataProvenanceExportVendorFieldOptions,
    normalizeMarketDataProvenanceExportSort,
    filteredFocusedMarketProviderProvenanceEvents,
    focusedMarketProviderProvenanceCount,
    formatMarketDataProvenanceExportFilterSummary,
    formatTimestamp,
    formatWorkflowToken,
  } = model;

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
            <option value={ALL_FILTER_VALUE}>전체 Provider</option>
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
            <option value={ALL_FILTER_VALUE}>전체 vendor field</option>
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
            <option value="newest">최신순</option>
            <option value="oldest">오래된순</option>
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
            placeholder="summary, provider, path 검색"
            type="search"
            value={marketDataProvenanceExportFilter.search_query}
          />
        </label>
      </div>
      <div className="run-filter-summary-chip-row">
        <span className="run-filter-summary-chip">
          필터 결과 {filteredFocusedMarketProviderProvenanceEvents.length}건
        </span>
        <span className="run-filter-summary-chip">
          전체 Provenance incident {focusedMarketProviderProvenanceCount}건
        </span>
        <span className="run-filter-summary-chip">
          {formatMarketDataProvenanceExportFilterSummary(marketDataProvenanceExportFilter)}
        </span>
      </div>
      {filteredFocusedMarketProviderProvenanceEvents.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>시각</th>
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
                      : "기록된 external reference가 없습니다."}
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
          현재 export 필터에 맞는 Provider provenance incident가 없습니다.
        </p>
      )}
    </>
  );
}
