// @ts-nocheck
export function RuntimeProviderProvenanceSharedRegistryAuditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
