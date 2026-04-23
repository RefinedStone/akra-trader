// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationCatalogLifecycleSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
                  <strong>Scheduler moderation policy catalogs</strong>
                  <p>
                    Save reusable moderation defaults and route selected feedback through a staged
                    approval queue before it changes learned ranking.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Name</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          name: event.target.value,
                        }));
                      }}
                      placeholder="Pending scheduler approvals"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.name}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          description: event.target.value,
                        }));
                      }}
                      placeholder="Moderate high-signal scheduler feedback before tuning"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.description}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Default outcome</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.default_moderation_status}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          default_moderation_status: event.target.value,
                        }));
                      }}
                    >
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="pending">Pending</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance view</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.governance_view}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          governance_view: event.target.value,
                        }));
                      }}
                    >
                      <option value="pending_queue">Pending queue</option>
                      <option value="stale_pending">Stale pending</option>
                      <option value="high_score_pending">High-score pending</option>
                      <option value="conflicting_queries">Conflicting queries</option>
                      <option value="all_feedback">All feedback</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Window</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.window_days}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          window_days: Number.parseInt(event.target.value, 10) || 30,
                        }));
                      }}
                    >
                      {[14, 30, 60, 90].map((value) => (
                        <option key={`provider-scheduler-search-policy-window-${value}`} value={value}>
                          {value}d
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Stale pending</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.stale_pending_hours}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                        }));
                      }}
                    >
                      {[12, 24, 48, 72].map((value) => (
                        <option key={`provider-scheduler-search-policy-stale-${value}`} value={value}>
                          {value}h
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Minimum score</span>
                    <input
                      min={0}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          minimum_score: Math.max(Number.parseInt(event.target.value, 10) || 0, 0),
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.minimum_score}
                    />
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Require note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.require_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                          ...current,
                          require_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading}
                    onClick={() => {
                      void createProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry();
                    }}
                    type="button"
                  >
                    {editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? "Update policy catalog" : "Save policy catalog"}
                  </button>
                  {editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? (
                    <button
                      className="ghost-button"
                      onClick={() => {
                        resetProviderProvenanceSchedulerSearchModerationPolicyCatalogEditor();
                        setProviderProvenanceWorkspaceFeedback("Moderation policy catalog editor reset.");
                      }}
                      type="button"
                    >
                      Cancel edit
                    </button>
                  ) : null}
                </div>
                <div className="market-data-provenance-history-actions">
                  <span className="run-lineage-symbol-copy">
                    {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length} selected
                  </span>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                      || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
                    }
                    onClick={() => {
                      void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("delete");
                    }}
                    type="button"
                  >
                    Delete selected
                  </button>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                      || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
                    }
                    onClick={() => {
                      void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("restore");
                    }}
                    type="button"
                  >
                    Restore selected
                  </button>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                      || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
                    }
                    onClick={() => {
                      void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("update");
                    }}
                    type="button"
                  >
                    Bulk edit
                  </button>
                  <label className="run-form-field">
                    <span>Name prefix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                          ...current,
                          name_prefix: event.target.value,
                        }));
                      }}
                      placeholder="[Ops] "
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.name_prefix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name suffix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                          ...current,
                          name_suffix: event.target.value,
                        }));
                      }}
                      placeholder=" / reviewed"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.name_suffix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description append</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                          ...current,
                          description_append: event.target.value,
                        }));
                      }}
                      placeholder="Bulk-governed in control room"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.description_append}
                    />
                  </label>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>
                        <input
                          aria-label="Select all moderation policy catalogs"
                          checked={
                            (providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ?? 0) > 0
                            && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                              === (providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ?? 0)
                          }
                          onChange={toggleAllProviderProvenanceSchedulerSearchModerationPolicyCatalogSelections}
                          type="checkbox"
                        />
                      </th>
                      <th>Catalog</th>
                      <th>Defaults</th>
                      <th>Governance</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ? (
                      providerProvenanceSchedulerSearchModerationPolicyCatalogs.items.map((entry) => (
                        <tr key={`provider-scheduler-search-policy-catalog-${entry.catalog_id}`}>
                          <td className="provider-provenance-selection-cell">
                            <input
                              aria-label={`Select moderation policy catalog ${entry.name}`}
                              checked={selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.includes(entry.catalog_id)}
                              onChange={() => {
                                toggleProviderProvenanceSchedulerSearchModerationPolicyCatalogSelection(entry.catalog_id);
                              }}
                              type="checkbox"
                            />
                          </td>
                          <td>
                            <strong>{entry.name}</strong>
                            <p className="run-lineage-symbol-copy">
                              {entry.description || "No description"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {shortenIdentifier(entry.catalog_id, 10)} · created {formatTimestamp(entry.created_at)}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                              {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                            </p>
                          </td>
                          <td>
                            <p className="run-lineage-symbol-copy">
                              Outcome {formatWorkflowToken(entry.default_moderation_status)}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Minimum score {entry.minimum_score} · note {entry.require_note ? "required" : "optional"}
                            </p>
                          </td>
                          <td>
                            <p className="run-lineage-symbol-copy">
                              View {formatWorkflowToken(entry.governance_view)}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Window {entry.window_days}d · stale {entry.stale_pending_hours}h
                            </p>
                          </td>
                          <td>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={entry.status !== "active"}
                                onClick={() => {
                                  void editProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry(entry);
                                }}
                                type="button"
                              >
                                Edit
                              </button>
                              <button
                                className="ghost-button"
                                disabled={entry.status !== "active"}
                                onClick={() => {
                                  void deleteProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry(entry);
                                }}
                                type="button"
                              >
                                Delete
                              </button>
                              <button
                                className="ghost-button"
                                onClick={() => {
                                  if (
                                    selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId === entry.catalog_id
                                    && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory
                                  ) {
                                    setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId(null);
                                    setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory(null);
                                    setProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryError(null);
                                  } else {
                                    void loadProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory(entry.catalog_id);
                                  }
                                }}
                                type="button"
                              >
                                {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId === entry.catalog_id
                                  && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory
                                  ? "Hide versions"
                                  : "Versions"}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5}>
                          <p className="empty-state">
                            No scheduler moderation policy catalogs saved yet.
                          </p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? (
                  <div className="market-data-provenance-shared-history">
                    <div className="market-data-provenance-history-head">
                      <strong>Scheduler moderation policy catalog revisions</strong>
                      <p>Inspect immutable catalog snapshots and restore a previous moderation governance revision.</p>
                    </div>
                    {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryLoading ? (
                      <p className="empty-state">Loading moderation policy catalog revisions…</p>
                    ) : null}
                    {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError ? (
                      <p className="market-data-workflow-feedback">
                        Moderation policy catalog revisions failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError}
                      </p>
                    ) : null}
                    {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory ? (
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>When</th>
                            <th>Snapshot</th>
                            <th>Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory.history.map((entry) => (
                            <tr key={entry.revision_id}>
                              <td>
                                <strong>{formatTimestamp(entry.recorded_at)}</strong>
                                <p className="run-lineage-symbol-copy">
                                  {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                                </p>
                              </td>
                              <td>
                                <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                                <p className="run-lineage-symbol-copy">{entry.name}</p>
                                <p className="run-lineage-symbol-copy">
                                  Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                                </p>
                                <p className="run-lineage-symbol-copy">
                                  Window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                                </p>
                                <p className="run-lineage-symbol-copy">{entry.reason}</p>
                              </td>
                              <td>
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    void restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryRevision(entry.revision_id);
                                  }}
                                  type="button"
                                >
                                  Restore revision
                                </button>
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
                    <strong>Scheduler moderation policy catalog team audit</strong>
                    <p>Filter lifecycle and bulk-governance events by catalog, action, actor, or search text.</p>
                  </div>
                  <div className="filter-bar">
                    <label>
                      <span>Catalog</span>
                      <select
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                            ...current,
                            catalog_id: event.target.value,
                          }))
                        }
                        value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.catalog_id}
                      >
                        <option value="">All catalogs</option>
                        {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                          <option key={entry.catalog_id} value={entry.catalog_id}>
                            {entry.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      <span>Action</span>
                      <select
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                            ...current,
                            action: event.target.value,
                          }))
                        }
                        value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.action}
                      >
                        <option value={ALL_FILTER_VALUE}>All actions</option>
                        <option value="created">Created</option>
                        <option value="updated">Updated</option>
                        <option value="deleted">Deleted</option>
                        <option value="restored">Restored</option>
                        <option value="bulk_updated">Bulk updated</option>
                        <option value="bulk_deleted">Bulk deleted</option>
                        <option value="bulk_restored">Bulk restored</option>
                      </select>
                    </label>
                    <label>
                      <span>Actor tab</span>
                      <input
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                            ...current,
                            actor_tab_id: event.target.value,
                          }))
                        }
                        placeholder="control-room"
                        type="text"
                        value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.actor_tab_id}
                      />
                    </label>
                    <label>
                      <span>Search</span>
                      <input
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                            ...current,
                            search: event.target.value,
                          }))
                        }
                        placeholder="high-score pending"
                        type="text"
                        value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.search}
                      />
                    </label>
                  </div>
                  {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading ? (
                    <p className="empty-state">Loading scheduler moderation policy catalog audit…</p>
                  ) : null}
                  {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError ? (
                    <p className="market-data-workflow-feedback">
                      Scheduler moderation policy catalog audit failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError}
                    </p>
                  ) : null}
                  {providerProvenanceSchedulerSearchModerationPolicyCatalogAudits.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Action</th>
                          <th>Detail</th>
                        </tr>
                      </thead>
                      <tbody>
                        {providerProvenanceSchedulerSearchModerationPolicyCatalogAudits.map((entry) => (
                          <tr key={entry.audit_id}>
                            <td>
                              <strong>{formatTimestamp(entry.recorded_at)}</strong>
                              <p className="run-lineage-symbol-copy">
                                {entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}
                              </p>
                            </td>
                            <td>
                              <strong>{formatWorkflowToken(entry.action)}</strong>
                              <p className="run-lineage-symbol-copy">{entry.name}</p>
                              <p className="run-lineage-symbol-copy">
                                {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.default_moderation_status)}
                              </p>
                            </td>
                            <td>
                              <p className="run-lineage-symbol-copy">{entry.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                              </p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    !providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading ? (
                      <p className="empty-state">No moderation policy catalog audit rows match the current filter.</p>
                    ) : null
                  )}
                </div>
    </>
  );
}
