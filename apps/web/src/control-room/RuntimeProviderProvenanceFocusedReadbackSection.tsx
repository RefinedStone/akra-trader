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
          <span>제공처</span>
          <select
            onChange={(event) =>
              setMarketDataProvenanceExportFilter((current) => ({
                ...current,
                provider: event.target.value,
              }))
            }
            value={marketDataProvenanceExportFilter.provider}
          >
            <option value={ALL_FILTER_VALUE}>전체 제공처</option>
            {marketDataProvenanceExportProviderOptions.map((provider) => (
              <option key={provider} value={provider}>
                {provider}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>제공처 필드</span>
          <select
            onChange={(event) =>
              setMarketDataProvenanceExportFilter((current) => ({
                ...current,
                vendor_field: event.target.value,
              }))
            }
            value={marketDataProvenanceExportFilter.vendor_field}
          >
            <option value={ALL_FILTER_VALUE}>전체 제공처 필드</option>
            {marketDataProvenanceExportVendorFieldOptions.map((vendorField) => (
              <option key={vendorField} value={vendorField}>
                {vendorField}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>정렬</span>
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
            <option value="provider">제공처</option>
            <option value="severity">심각도</option>
          </select>
        </label>
        <label>
          <span>검색</span>
          <input
            onChange={(event) =>
              setMarketDataProvenanceExportFilter((current) => ({
                ...current,
                search_query: event.target.value,
              }))
            }
            placeholder="요약, 제공처, 경로 검색"
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
          전체 제공처 문제 {focusedMarketProviderProvenanceCount}건
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
              <th>제공처</th>
              <th>상태</th>
              <th>근거</th>
            </tr>
          </thead>
          <tbody>
            {filteredFocusedMarketProviderProvenanceEvents.slice(0, 8).map((record) => (
              <tr key={`provider-provenance-${record.event.event_id}`}>
                <td>{formatTimestamp(record.event.timestamp)}</td>
                <td>
                  <strong>{record.provider}</strong>
                  <p className="run-lineage-symbol-copy">
                    제공처 필드: {record.vendorField}
                  </p>
                </td>
                <td>
                  <strong>{record.event.summary}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(record.event.kind)} / {formatWorkflowToken(record.event.severity)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {record.event.external_reference
                      ? `외부 참조: ${record.event.external_reference}`
                      : "기록된 외부 참조가 없습니다."}
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
          현재 내보내기 필터에 맞는 제공처 문제가 없습니다.
        </p>
      )}
    </>
  );
}
