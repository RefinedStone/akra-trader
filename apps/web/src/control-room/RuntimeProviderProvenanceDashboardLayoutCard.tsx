// @ts-nocheck
export function RuntimeProviderProvenanceDashboardLayoutCard({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Dashboard layout</strong>
        <p>Save and replay the current analytics layout as a shared dashboard view.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Highlight</span>
          <select
            onChange={(event) =>
              setProviderProvenanceDashboardLayout((current) => ({
                ...current,
                highlight_panel:
                  event.target.value === "drift" ||
                  event.target.value === "burn_up" ||
                  event.target.value === "rollups" ||
                  event.target.value === "scheduler_alerts" ||
                  event.target.value === "recent_exports"
                    ? event.target.value
                    : "overview",
              }))
            }
            value={providerProvenanceDashboardLayout.highlight_panel}
          >
            <option value="overview">Overview</option>
            <option value="drift">Drift</option>
            <option value="burn_up">Burn-up</option>
            <option value="rollups">Rollups</option>
            <option value="scheduler_alerts">Scheduler alerts</option>
            <option value="recent_exports">Recent exports</option>
          </select>
        </label>
        <label className="provider-provenance-checkbox">
          <input
            checked={providerProvenanceDashboardLayout.show_time_series}
            onChange={(event) =>
              setProviderProvenanceDashboardLayout((current) => ({
                ...current,
                show_time_series: event.target.checked,
              }))
            }
            type="checkbox"
          />
          <span>Show time series</span>
        </label>
        <label className="provider-provenance-checkbox">
          <input
            checked={providerProvenanceDashboardLayout.show_rollups}
            onChange={(event) =>
              setProviderProvenanceDashboardLayout((current) => ({
                ...current,
                show_rollups: event.target.checked,
              }))
            }
            type="checkbox"
          />
          <span>Show rollups</span>
        </label>
        <label className="provider-provenance-checkbox">
          <input
            checked={providerProvenanceDashboardLayout.show_recent_exports}
            onChange={(event) =>
              setProviderProvenanceDashboardLayout((current) => ({
                ...current,
                show_recent_exports: event.target.checked,
              }))
            }
            type="checkbox"
          />
          <span>Show recent exports</span>
        </label>
      </div>
      {providerProvenanceWorkspaceFeedback ? (
        <p className="market-data-workflow-feedback">{providerProvenanceWorkspaceFeedback}</p>
      ) : null}
    </div>
  );
}
