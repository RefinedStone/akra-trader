// @ts-nocheck
export function RuntimeProviderProvenanceAnalyticsPresetsCard({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Saved analytics presets</strong>
        <p>Save the current analytics query as a server-side preset and re-apply it later.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenancePresetDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="BTC drift watch"
            type="text"
            value={providerProvenancePresetDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenancePresetDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="current focus drift query"
            type="text"
            value={providerProvenancePresetDraft.description}
          />
        </label>
        <label>
          <span>Action</span>
          <button
            className="ghost-button"
            onClick={() => {
              void saveCurrentProviderProvenancePreset();
            }}
            type="button"
          >
            Save preset
          </button>
        </label>
      </div>
      {providerProvenanceAnalyticsPresetsLoading ? (
        <p className="empty-state">Loading analytics presets…</p>
      ) : null}
      {providerProvenanceAnalyticsPresetsError ? (
        <p className="market-data-workflow-feedback">
          Preset registry load failed: {providerProvenanceAnalyticsPresetsError}
        </p>
      ) : null}
      {providerProvenanceAnalyticsPresets.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Preset</th>
              <th>Filter</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceAnalyticsPresets.slice(0, 6).map((entry) => (
              <tr key={entry.preset_id}>
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.focus.symbol ?? "all symbols"} · {entry.focus.timeframe ?? "all windows"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <strong>{entry.filter_summary}</strong>
                  <p className="run-lineage-symbol-copy">Updated {formatTimestamp(entry.updated_at)}</p>
                </td>
                <td>
                  <button
                    className="ghost-button"
                    onClick={() => {
                      void applyProviderProvenanceWorkspaceQuery(entry, {
                        includeLayout: false,
                        feedbackLabel: `Preset ${entry.name}`,
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
        <p className="empty-state">No server-side analytics presets saved yet.</p>
      )}
    </div>
  );
}
