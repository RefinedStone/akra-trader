// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueueCard } from "./RuntimeProviderProvenanceApprovalQueueCard";
import { RuntimeProviderProvenanceScheduledReportsCard } from "./RuntimeProviderProvenanceScheduledReportsCard";
import { RuntimeProviderProvenanceGovernancePolicyTemplatesCard } from "./RuntimeProviderProvenanceGovernancePolicyTemplatesCard";
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryCard } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryCard";
import { RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard";

export function RuntimeProviderProvenanceWorkspaceCards({ model }: { model: any }) {
  const {} = model;

  return (
    <>
                                <div className="provider-provenance-workspace-card">
                                  <div className="market-data-provenance-history-head">
                                    <strong>Dashboard layout</strong>
                                    <p>
                                      Save and replay the current analytics layout as a shared dashboard view.
                                    </p>
                                  </div>
                                  <div className="filter-bar">
                                    <label>
                                      <span>Highlight</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceDashboardLayout((current) => ({
                                            ...current,
                                            highlight_panel:
                                              event.target.value === "drift"
                                              || event.target.value === "burn_up"
                                              || event.target.value === "rollups"
                                              || event.target.value === "scheduler_alerts"
                                              || event.target.value === "recent_exports"
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
                                    <p className="market-data-workflow-feedback">
                                      {providerProvenanceWorkspaceFeedback}
                                    </p>
                                  ) : null}
                                </div>
                                <RuntimeProviderProvenanceGovernancePolicyTemplatesCard model={model} />
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
                                              <p className="run-lineage-symbol-copy">
                                                Updated {formatTimestamp(entry.updated_at)}
                                              </p>
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
                                <div className="provider-provenance-workspace-card">
                                  <div className="market-data-provenance-history-head">
                                    <strong>Shared dashboard views</strong>
                                    <p>Store the current analytics query together with the chosen layout emphasis and any scheduler approval queue slice.</p>
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
                                              <p className="run-lineage-symbol-copy">
                                                {entry.filter_summary}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.preset_id ? `Preset ${shortenIdentifier(entry.preset_id, 10)}` : "No preset link"}
                                              </p>
                                            </td>
                                            <td>
                                              <strong>{entry.layout.highlight_panel}</strong>
                                              <p className="run-lineage-symbol-copy">
                                                {entry.layout.show_time_series ? "time series" : "no time series"} · {" "}
                                                {entry.layout.show_rollups ? "rollups" : "no rollups"} · {" "}
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
                                <RuntimeProviderProvenanceScheduledReportsCard model={model} />
                                <RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard model={model} />
                                <RuntimeProviderProvenanceSchedulerNarrativeRegistryCard model={model} />
                                <RuntimeProviderProvenanceApprovalQueueCard model={model} />
    </>
  );
}
