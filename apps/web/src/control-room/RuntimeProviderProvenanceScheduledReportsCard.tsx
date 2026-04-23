// @ts-nocheck
export function RuntimeProviderProvenanceScheduledReportsCard({ model }: { model: any }) {
  const {
    applyProviderProvenanceWorkspaceQuery,
    copyProviderProvenanceExportJobById,
    createCurrentProviderProvenanceScheduledReport,
    formatTimestamp,
    providerProvenanceAnalyticsPresets,
    providerProvenanceDashboardViews,
    providerProvenanceReportDraft,
    providerProvenanceScheduledReportHistoryError,
    providerProvenanceScheduledReportHistoryLoading,
    providerProvenanceScheduledReports,
    providerProvenanceScheduledReportsError,
    providerProvenanceScheduledReportsLoading,
    runDueSharedProviderProvenanceScheduledReports,
    runSharedProviderProvenanceScheduledReport,
    selectedProviderProvenanceScheduledReportHistory,
    selectedProviderProvenanceScheduledReportId,
    setProviderProvenanceReportDraft,
    shortenIdentifier,
    toggleProviderProvenanceScheduledReportHistory,
  } = model;

  return (
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
                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                  <p className="run-lineage-symbol-copy">
                    {entry.view_id ? `View ${shortenIdentifier(entry.view_id, 10)}` : "No view link"}
                  </p>
                </td>
                <td>
                  <strong>{entry.status} · {entry.cadence}</strong>
                  <p className="run-lineage-symbol-copy">Next {formatTimestamp(entry.next_run_at)}</p>
                  <p className="run-lineage-symbol-copy">Last {formatTimestamp(entry.last_run_at)}</p>
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
            <p>Review report runs and copy any generated analytics export artifact.</p>
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
  );
}
