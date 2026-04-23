// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportSavedViewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Saved stitched report views</strong>
        <p>
          Store stitched multi-occurrence scheduler report slices as reusable saved views,
          then re-apply, copy, download, or share them without rebuilding the filter set by
          hand.
        </p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Lag recovery stitched report"
            type="text"
            value={providerProvenanceSchedulerStitchedReportViewDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="saved stitched occurrence slice"
            type="text"
            value={providerProvenanceSchedulerStitchedReportViewDraft.description}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveCurrentProviderProvenanceSchedulerStitchedReportView();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerStitchedReportViewId
                ? "Save changes"
                : "Save stitched view"}
            </button>
            {editingProviderProvenanceSchedulerStitchedReportViewId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerStitchedReportViewDraft();
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
        </label>
      </div>
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <div className="provider-provenance-governance-bar">
          <div className="provider-provenance-governance-summary">
            <strong>
              {selectedProviderProvenanceSchedulerStitchedReportViewIds.length} selected
            </strong>
            <span>
              {selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter((entry) => entry.status === "active").length} active · {" "}
              {selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter((entry) => entry.status === "deleted").length} deleted
            </span>
          </div>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
              type="button"
            >
              {selectedProviderProvenanceSchedulerStitchedReportViewIds.length === providerProvenanceSchedulerStitchedReportViews.length
                ? "Clear all"
                : "Select all"}
            </button>
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerStitchedReportViewIds.length || providerProvenanceSchedulerStitchedReportViewBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("delete");
              }}
              type="button"
            >
              {providerProvenanceSchedulerStitchedReportViewBulkAction === "delete"
                ? "Previewing…"
                : "Preview delete"}
            </button>
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerStitchedReportViewIds.length || providerProvenanceSchedulerStitchedReportViewBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("restore");
              }}
              type="button"
            >
              {providerProvenanceSchedulerStitchedReportViewBulkAction === "restore"
                ? "Previewing…"
                : "Preview restore"}
            </button>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Bulk stitched view edits</strong>
            <p>Preview metadata, scheduler slice filters, and export-limit changes across multiple saved stitched report views, then approve and apply the staged plan.</p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Name prefix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }))
                }
                placeholder="Ops / "
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.name_prefix}
              />
            </label>
            <label>
              <span>Name suffix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }))
                }
                placeholder=" / v2"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.name_suffix}
              />
            </label>
            <label>
              <span>Description append</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }))
                }
                placeholder="reviewed in shift handoff"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.description_append}
              />
            </label>
            <label>
              <span>Category</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_category: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_category}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>All categories</option>
                <option value="scheduler_lag">scheduler lag</option>
                <option value="scheduler_failure">scheduler failure</option>
              </select>
            </label>
            <label>
              <span>Status</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_status: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_status}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>All statuses</option>
                <option value="active">active</option>
                <option value="resolved">resolved</option>
              </select>
            </label>
            <label>
              <span>Facet</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_narrative_facet:
                      event.target.value === "resolved_narratives"
                      || event.target.value === "post_resolution_recovery"
                      || event.target.value === "recurring_occurrences"
                      || event.target.value === "all_occurrences"
                        ? event.target.value
                        : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_narrative_facet}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="all_occurrences">all occurrences</option>
                <option value="resolved_narratives">resolved narratives</option>
                <option value="post_resolution_recovery">post-resolution recovery</option>
                <option value="recurring_occurrences">recurring occurrences</option>
              </select>
            </label>
            <label>
              <span>Window days</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    window_days: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.window_days}
              />
            </label>
            <label>
              <span>Result limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    result_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.result_limit}
              />
            </label>
            <label>
              <span>Occurrence limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    occurrence_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.occurrence_limit}
              />
            </label>
            <label>
              <span>History limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    history_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.history_limit}
              />
            </label>
            <label>
              <span>Drill-down limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    drilldown_history_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.drilldown_history_limit}
              />
            </label>
            <label>
              <span>Policy template</span>
              <select
                onChange={(event) => {
                  setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId(
                    event.target.value,
                  );
                }}
                value={providerProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId}
              >
                <option value="">Default staged policy</option>
                {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                  .filter(
                    (entry) =>
                      entry.status === "active"
                      && providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                        entry.item_type_scope,
                        "stitched_report_view",
                      ),
                  )
                  .map((entry) => (
                    <option key={entry.policy_template_id} value={entry.policy_template_id}>
                      {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              <span>Action</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerStitchedReportViewIds.length || providerProvenanceSchedulerStitchedReportViewBulkAction !== null}
                  onClick={() => {
                    void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("update");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerStitchedReportViewBulkAction === "update"
                    ? "Previewing…"
                    : "Preview bulk edit"}
                </button>
              </div>
            </label>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViewsLoading ? (
        <p className="empty-state">Loading stitched report views…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViewsError ? (
        <p className="market-data-workflow-feedback">
          Stitched report views failed: {providerProvenanceSchedulerStitchedReportViewsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all stitched report views"
                  checked={
                    providerProvenanceSchedulerStitchedReportViews.length > 0
                    && selectedProviderProvenanceSchedulerStitchedReportViewIds.length === providerProvenanceSchedulerStitchedReportViews.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
                  type="checkbox"
                />
              </th>
              <th>View</th>
              <th>Slice</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerStitchedReportViews.map((entry) => (
              <tr key={`provider-scheduler-stitched-view-${entry.view_id}`}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select stitched report view ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerStitchedReportViewIdSet.has(entry.view_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerStitchedReportViewSelection(entry.view_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                  <p className="run-lineage-symbol-copy">
                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"} · updated{" "}
                    {formatTimestamp(entry.updated_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                    {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                  </p>
                </td>
                <td>
                  <strong>{entry.occurrence_limit} occurrence(s)</strong>
                  <p className="run-lineage-symbol-copy">
                    History {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Focus {entry.query.focus_scope === "current_focus" ? "current focus" : "all focuses"}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        void applyProviderProvenanceSchedulerStitchedReportView(entry);
                      }}
                      type="button"
                    >
                      Apply
                    </button>
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        void editProviderProvenanceSchedulerStitchedReportView(entry);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        void deleteProviderProvenanceSchedulerStitchedReportViewEntry(entry);
                      }}
                      type="button"
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void toggleProviderProvenanceSchedulerStitchedReportViewHistory(entry.view_id);
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerStitchedReportViewId === entry.view_id
                        && selectedProviderProvenanceSchedulerStitchedReportViewHistory
                        ? "Hide versions"
                        : "Versions"}
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void copyProviderProvenanceSchedulerStitchedNarrativeReportView(entry);
                      }}
                      type="button"
                    >
                      Copy report
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void downloadProviderProvenanceSchedulerStitchedNarrativeCsvView(entry);
                      }}
                      type="button"
                    >
                      Download CSV
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void shareProviderProvenanceSchedulerStitchedNarrativeReportView(entry);
                      }}
                      type="button"
                    >
                      Share report
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No stitched scheduler report views saved yet.</p>
      )}
      {selectedProviderProvenanceSchedulerStitchedReportViewId ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Stitched report view revisions</strong>
            <p>Inspect immutable saved-view snapshots, apply them to the workbench, or restore them as the active stitched report view.</p>
          </div>
          {providerProvenanceSchedulerStitchedReportViewHistoryLoading ? (
            <p className="empty-state">Loading stitched report view revisions…</p>
          ) : null}
          {providerProvenanceSchedulerStitchedReportViewHistoryError ? (
            <p className="market-data-workflow-feedback">
              Stitched report view revisions failed: {providerProvenanceSchedulerStitchedReportViewHistoryError}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerStitchedReportViewHistory ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Snapshot</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {selectedProviderProvenanceSchedulerStitchedReportViewHistory.history.map((entry) => (
                  <tr key={entry.revision_id}>
                    <td>
                      <strong>{formatTimestamp(entry.recorded_at)}</strong>
                      <p className="run-lineage-symbol-copy">
                        {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                      </p>
                    </td>
                    <td>
                      <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                      <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                      <p className="run-lineage-symbol-copy">
                        {entry.occurrence_limit} occurrence(s) · history {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                      </p>
                      <p className="run-lineage-symbol-copy">{entry.reason}</p>
                    </td>
                    <td>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          onClick={() => {
                            void applyProviderProvenanceWorkspaceQuery(entry, {
                              includeLayout: false,
                              forceSchedulerHighlight: true,
                              feedbackLabel: `Stitched report revision ${entry.revision_id}`,
                            });
                          }}
                          type="button"
                        >
                          Apply snapshot
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            void restoreProviderProvenanceSchedulerStitchedReportViewHistoryRevision(entry);
                          }}
                          type="button"
                        >
                          Restore revision
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </div>
      ) : null}
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched report view team audit</strong>
          <p>Filter shared audit rows by saved view, action, or actor to review bulk governance and lifecycle changes.</p>
        </div>
        <div className="filter-bar">
          <label>
            <span>View</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                  ...current,
                  view_id: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportViewAuditFilter.view_id}
            >
              <option value="">All views</option>
              {providerProvenanceSchedulerStitchedReportViews.map((entry) => (
                <option key={entry.view_id} value={entry.view_id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Action</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                  ...current,
                  action: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportViewAuditFilter.action}
            >
              <option value={ALL_FILTER_VALUE}>All actions</option>
              <option value="created">Created</option>
              <option value="updated">Updated</option>
              <option value="deleted">Deleted</option>
              <option value="restored">Restored</option>
            </select>
          </label>
          <label>
            <span>Actor tab</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                  ...current,
                  actor_tab_id: event.target.value,
                }))
              }
              placeholder="tab_ops"
              type="text"
              value={providerProvenanceSchedulerStitchedReportViewAuditFilter.actor_tab_id}
            />
          </label>
          <label>
            <span>Search</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportViewAuditFilter((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
              placeholder="lag recovery"
              type="text"
              value={providerProvenanceSchedulerStitchedReportViewAuditFilter.search}
            />
          </label>
        </div>
        {providerProvenanceSchedulerStitchedReportViewAuditsLoading ? (
          <p className="empty-state">Loading stitched report view audit…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportViewAuditsError ? (
          <p className="market-data-workflow-feedback">
            Stitched report view audit failed: {providerProvenanceSchedulerStitchedReportViewAuditsError}
          </p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportViewAudits.length ? (
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
              {providerProvenanceSchedulerStitchedReportViewAudits.map((entry) => (
                <tr key={`provider-scheduler-stitched-view-audit-${entry.audit_id}`}>
                  <td>
                    <strong>{formatTimestamp(entry.recorded_at)}</strong>
                    <p className="run-lineage-symbol-copy">{entry.name}</p>
                  </td>
                  <td>
                    <strong>{formatWorkflowToken(entry.action)}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(entry.status)} · {entry.filter_summary}
                    </p>
                  </td>
                  <td>
                    <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}</strong>
                    <p className="run-lineage-symbol-copy">
                      {entry.actor_tab_id ?? "No tab id recorded."}
                    </p>
                  </td>
                  <td>
                    <strong>{entry.detail}</strong>
                    <p className="run-lineage-symbol-copy">{entry.reason}</p>
                    <p className="run-lineage-symbol-copy">
                      {entry.occurrence_limit} occurrence(s) · history {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
      ) : (
          !providerProvenanceSchedulerStitchedReportViewAuditsLoading
            ? <p className="empty-state">No stitched report view audit events match the selected filters.</p>
            : null
        )}
      </div>
    </>
  );
}

