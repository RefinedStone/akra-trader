// @ts-nocheck
export function RuntimeProviderProvenanceDashboardViewsCard({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Shared dashboard views</strong>
        <p>
          Store the current analytics query together with the chosen layout emphasis and any
          scheduler approval queue slice.
        </p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceViewDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="BTC drift board"
            type="text"
            value={providerProvenanceViewDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceViewDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="shared dashboard view"
            type="text"
            value={providerProvenanceViewDraft.description}
          />
        </label>
        <label>
          <span>Preset link</span>
          <select
            onChange={(event) =>
              setProviderProvenanceViewDraft((current) => ({
                ...current,
                preset_id: event.target.value,
              }))
            }
            value={providerProvenanceViewDraft.preset_id}
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
          <span>Action</span>
          <button
            className="ghost-button"
            onClick={() => {
              void saveCurrentProviderProvenanceDashboardView();
            }}
            type="button"
          >
            Save view
          </button>
        </label>
      </div>
      {providerProvenanceDashboardViewsLoading ? (
        <p className="empty-state">Loading dashboard views…</p>
      ) : null}
      {providerProvenanceDashboardViewsError ? (
        <p className="market-data-workflow-feedback">
          Dashboard view registry load failed: {providerProvenanceDashboardViewsError}
        </p>
      ) : null}
      {providerProvenanceDashboardViews.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>View</th>
              <th>Layout</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceDashboardViews.slice(0, 6).map((entry) => (
              <tr key={entry.view_id}>
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                  <p className="run-lineage-symbol-copy">
                    {entry.preset_id
                      ? `Preset ${shortenIdentifier(entry.preset_id, 10)}`
                      : "No preset link"}
                  </p>
                </td>
                <td>
                  <strong>{entry.layout.highlight_panel}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.layout.show_time_series ? "time series" : "no time series"} ·{" "}
                    {entry.layout.show_rollups ? "rollups" : "no rollups"} ·{" "}
                    {entry.layout.show_recent_exports ? "recent exports" : "no recent exports"}
                  </p>
                  {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                    entry.layout.governance_queue_view,
                  ) ? (
                    <p className="run-lineage-symbol-copy">
                      {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                        entry.layout.governance_queue_view,
                      )}
                    </p>
                  ) : null}
                </td>
                <td>
                  <button
                    className="ghost-button"
                    onClick={() => {
                      void applyProviderProvenanceWorkspaceQuery(entry, {
                        includeLayout: true,
                        feedbackLabel: `View ${entry.name}`,
                      });
                    }}
                    type="button"
                  >
                    Apply
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No shared dashboard views saved yet.</p>
      )}
    </div>
  );
}
