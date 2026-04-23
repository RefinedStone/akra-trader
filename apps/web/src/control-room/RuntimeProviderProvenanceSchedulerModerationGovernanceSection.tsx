// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationGovernanceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerSearchDashboard ? (
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
                <div className="market-data-provenance-history-head">
                  <strong>Moderation catalog governance policies</strong>
                  <p>
                    Save reusable approval requirements and update defaults, then stage
                    selected moderation policy catalogs through a dedicated governance queue.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Name</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          name: event.target.value,
                        }));
                      }}
                      placeholder="Catalog cleanup with approval"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Action scope</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.action_scope}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          action_scope: event.target.value,
                        }));
                      }}
                    >
                      <option value="any">Any action</option>
                      <option value="update">Update only</option>
                      <option value="delete">Delete only</option>
                      <option value="restore">Restore only</option>
                    </select>
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Require approval note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.require_approval_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          require_approval_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          description: event.target.value,
                        }));
                      }}
                      placeholder="Stage policy-catalog changes behind explicit approval."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.description}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Guidance</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          guidance: event.target.value,
                        }));
                      }}
                      placeholder="Require note before catalog lifecycle changes."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.guidance}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name prefix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          name_prefix: event.target.value,
                        }));
                      }}
                      placeholder="[Ops] "
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name_prefix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name suffix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          name_suffix: event.target.value,
                        }));
                      }}
                      placeholder=" / reviewed"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name_suffix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description append</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          description_append: event.target.value,
                        }));
                      }}
                      placeholder=" Escalate stale pending rows before applying."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.description_append}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Default outcome</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.default_moderation_status}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
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
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.governance_view}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
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
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.window_days}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          window_days: Number.parseInt(event.target.value, 10) || 30,
                        }));
                      }}
                    >
                      {[14, 30, 60, 90].map((value) => (
                        <option key={`provider-scheduler-search-governance-policy-window-${value}`} value={value}>
                          {value}d
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Stale pending</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.stale_pending_hours}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                        }));
                      }}
                    >
                      {[12, 24, 48, 72].map((value) => (
                        <option key={`provider-scheduler-search-governance-policy-stale-${value}`} value={value}>
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
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          minimum_score: Math.max(Number.parseInt(event.target.value, 10) || 0, 0),
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.minimum_score}
                    />
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Require moderation note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.require_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                          ...current,
                          require_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading}
                    onClick={() => {
                      void createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry();
                    }}
                    type="button"
                  >
                    {editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? "Update governance policy" : "Save governance policy"}
                  </button>
                  {editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? (
                    <button
                      className="ghost-button"
                      onClick={() => {
                        resetProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEditor();
                        setProviderProvenanceWorkspaceFeedback("Moderation governance policy editor reset.");
                      }}
                      type="button"
                    >
                      Cancel edit
                    </button>
                  ) : null}
                </div>
                <div className="market-data-provenance-history-actions">
                  <span className="run-lineage-symbol-copy">
                    {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length} selected
                  </span>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
                    }
                    onClick={() => {
                      void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("delete");
                    }}
                    type="button"
                  >
                    Delete selected
                  </button>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
                    }
                    onClick={() => {
                      void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("restore");
                    }}
                    type="button"
                  >
                    Restore selected
                  </button>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
                    }
                    onClick={() => {
                      void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("update");
                    }}
                    type="button"
                  >
                    Bulk edit
                  </button>
                  <label className="run-form-field">
                    <span>Name prefix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                          ...current,
                          name_prefix: event.target.value,
                        }));
                      }}
                      placeholder="[Ops] "
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.name_prefix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name suffix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                          ...current,
                          name_suffix: event.target.value,
                        }));
                      }}
                      placeholder=" / reviewed"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.name_suffix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Guidance</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                          ...current,
                          guidance: event.target.value,
                        }));
                      }}
                      placeholder="Require explicit review before apply."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.guidance}
                    />
                  </label>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>
                        <input
                          aria-label="Select all moderation governance policies"
                          checked={
                            (providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ?? 0) > 0
                            && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                              === (providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ?? 0)
                          }
                          onChange={toggleAllProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelections}
                          type="checkbox"
                        />
                      </th>
                      <th>Policy</th>
                      <th>Defaults</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-governance-policy-${entry.governance_policy_id}`}>
                          <td className="provider-provenance-selection-cell">
                            <input
                              aria-label={`Select moderation governance policy ${entry.name}`}
                              checked={selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.includes(entry.governance_policy_id)}
                              onChange={() => {
                                toggleProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelection(entry.governance_policy_id);
                              }}
                              type="checkbox"
                            />
                          </td>
                          <td>
                            <strong>{entry.name}</strong>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.action_scope)} · approval note {entry.require_approval_note ? "required" : "optional"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.guidance || entry.description || "No governance guidance"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                              {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                            </p>
                          </td>
                          <td>
                            <p className="run-lineage-symbol-copy">
                              {entry.name_prefix || entry.name_suffix
                                ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                                : "No name affixes"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                            </p>
                          </td>
                          <td>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={entry.status !== "active"}
                                onClick={() => {
                                  void editProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry(entry);
                                }}
                                type="button"
                              >
                                Edit
                              </button>
                              <button
                                className="ghost-button"
                                disabled={entry.status !== "active"}
                                onClick={() => {
                                  void deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry(entry);
                                }}
                                type="button"
                              >
                                Delete
                              </button>
                              <button
                                className="ghost-button"
                                onClick={() => {
                                  if (
                                    selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId === entry.governance_policy_id
                                    && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory
                                  ) {
                                    setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId(null);
                                    setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory(null);
                                    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError(null);
                                  } else {
                                    void loadProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory(entry.governance_policy_id);
                                  }
                                }}
                                type="button"
                              >
                                {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId === entry.governance_policy_id
                                  && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory
                                  ? "Hide versions"
                                  : "Versions"}
                              </button>
                              <button
                                className="ghost-button"
                                onClick={() => {
                                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                                    ...current,
                                    governance_policy_id: entry.governance_policy_id,
                                    action:
                                      entry.action_scope === "update"
                                      || entry.action_scope === "delete"
                                      || entry.action_scope === "restore"
                                        ? entry.action_scope
                                        : current.action,
                                  }));
                                  setProviderProvenanceWorkspaceFeedback(
                                    `Selected moderation catalog governance policy ${entry.name}.`,
                                  );
                                }}
                                type="button"
                              >
                                Use policy
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4}>
                          <p className="empty-state">No moderation catalog governance policies saved yet.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? (
                  <div className="market-data-provenance-shared-history">
                    <div className="market-data-provenance-history-head">
                      <strong>Moderation governance policy revisions</strong>
                      <p>Inspect immutable policy snapshots and restore a previous governance default set.</p>
                    </div>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryLoading ? (
                      <p className="empty-state">Loading moderation governance policy revisions…</p>
                    ) : null}
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError ? (
                      <p className="market-data-workflow-feedback">
                        Moderation governance policy revisions failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError}
                      </p>
                    ) : null}
                    {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory ? (
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>When</th>
                            <th>Snapshot</th>
                            <th>Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory.history.map((entry) => (
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
                                  {formatWorkflowToken(entry.action_scope)} · approval note {entry.require_approval_note ? "required" : "optional"}
                                </p>
                                <p className="run-lineage-symbol-copy">
                                  Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                                </p>
                                <p className="run-lineage-symbol-copy">{entry.reason}</p>
                              </td>
                              <td>
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    void restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRevision(entry.revision_id);
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
                    <strong>Moderation governance policy team audit</strong>
                    <p>Filter lifecycle and bulk governance events by policy, action, actor, or search text.</p>
                  </div>
                  <div className="filter-bar">
                    <label>
                      <span>Policy</span>
                      <select
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                            ...current,
                            governance_policy_id: event.target.value,
                          }))
                        }
                        value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.governance_policy_id}
                      >
                        <option value="">All policies</option>
                        {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                          <option key={entry.governance_policy_id} value={entry.governance_policy_id}>
                            {entry.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      <span>Action</span>
                      <select
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                            ...current,
                            action: event.target.value,
                          }))
                        }
                        value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.action}
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
                          setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                            ...current,
                            actor_tab_id: event.target.value,
                          }))
                        }
                        placeholder="control-room"
                        type="text"
                        value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.actor_tab_id}
                      />
                    </label>
                    <label>
                      <span>Search</span>
                      <input
                        onChange={(event) =>
                          setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                            ...current,
                            search: event.target.value,
                          }))
                        }
                        placeholder="approval note"
                        type="text"
                        value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.search}
                      />
                    </label>
                  </div>
                  {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading ? (
                    <p className="empty-state">Loading moderation governance policy audit…</p>
                  ) : null}
                  {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError ? (
                    <p className="market-data-workflow-feedback">
                      Moderation governance policy audit failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError}
                    </p>
                  ) : null}
                  {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Action</th>
                          <th>Detail</th>
                        </tr>
                      </thead>
                      <tbody>
                        {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits.map((entry) => (
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
                                {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.action_scope)}
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
                    !providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading ? (
                      <p className="empty-state">No moderation governance policy audit rows match the current filter.</p>
                    ) : null
                  )}
                </div>
                <div className="market-data-provenance-history-head">
                  <strong>Moderation governance meta-policies</strong>
                  <p>
                    Save reusable review defaults for moderation governance policies, then
                    stage selected policy updates through a dedicated approval queue.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Name</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          name: event.target.value,
                        }));
                      }}
                      placeholder="Review moderation governance defaults"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Queue action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.action_scope}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          action_scope: event.target.value,
                        }));
                      }}
                    >
                      <option value="any">Any action</option>
                      <option value="update">Update only</option>
                      <option value="delete">Delete only</option>
                      <option value="restore">Restore only</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Policy action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_action_scope}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          policy_action_scope: event.target.value,
                        }));
                      }}
                    >
                      <option value="any">Any action</option>
                      <option value="update">Update only</option>
                      <option value="delete">Delete only</option>
                      <option value="restore">Restore only</option>
                    </select>
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Approval note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_approval_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          require_approval_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Policy note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_require_approval_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          policy_require_approval_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          description: event.target.value,
                        }));
                      }}
                      placeholder="Reusable defaults for moderation governance policy review."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Queue guidance</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          guidance: event.target.value,
                        }));
                      }}
                      placeholder="Require an explicit note before approval."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.guidance}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Policy guidance</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          policy_guidance: event.target.value,
                        }));
                      }}
                      placeholder="Apply these defaults to selected governance policies."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_guidance}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name prefix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          name_prefix: event.target.value,
                        }));
                      }}
                      placeholder="[Reviewed] "
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_prefix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name suffix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          name_suffix: event.target.value,
                        }));
                      }}
                      placeholder=" / approved"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_suffix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description append</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          description_append: event.target.value,
                        }));
                      }}
                      placeholder=" Reviewed in moderation governance queue."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description_append}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Outcome</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.default_moderation_status}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          default_moderation_status: event.target.value,
                        }));
                      }}
                    >
                      <option value="approved">Approved</option>
                      <option value="pending">Pending</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance view</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.governance_view}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          governance_view: event.target.value,
                        }));
                      }}
                    >
                      <option value="all_feedback">All feedback</option>
                      <option value="pending_queue">Pending queue</option>
                      <option value="high_score_pending">High-score pending</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Window days</span>
                    <input
                      min={7}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          window_days: Number(event.target.value) || 0,
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.window_days}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Stale pending hours</span>
                    <input
                      min={1}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          stale_pending_hours: Number(event.target.value) || 0,
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.stale_pending_hours}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Minimum score</span>
                    <input
                      min={0}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          minimum_score: Number(event.target.value) || 0,
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.minimum_score}
                    />
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Require moderator note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          require_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesLoading}
                    onClick={() => {
                      void createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry();
                    }}
                    type="button"
                  >
                    Save meta-policy
                  </button>
                </div>
                {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError ? (
                  <p className="market-data-workflow-feedback">
                    Moderation governance meta-policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError}
                  </p>
                ) : null}
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Meta-policy</th>
                      <th>Defaults</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-governance-meta-policy-${entry.meta_policy_id}`}>
                          <td>
                            <strong>{entry.name}</strong>
                            <p className="run-lineage-symbol-copy">
                              Queue {formatWorkflowToken(entry.action_scope)} · note {entry.require_approval_note ? "required" : "optional"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.guidance || entry.description || "No meta-governance guidance"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Saved {formatTimestamp(entry.updated_at)} · {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                            </p>
                          </td>
                          <td>
                            <p className="run-lineage-symbol-copy">
                              Policy {formatWorkflowToken(entry.policy_action_scope ?? "any")} · note {entry.policy_require_approval_note ? "required" : "optional"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Outcome {formatWorkflowToken(entry.default_moderation_status ?? "approved")} · view {formatWorkflowToken(entry.governance_view ?? "pending_queue")}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Window {entry.window_days ?? 0}d · stale {entry.stale_pending_hours ?? 0}h · minimum {entry.minimum_score ?? 0}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.name_prefix || entry.name_suffix
                                ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                                : "No name affixes"}
                            </p>
                          </td>
                          <td>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                onClick={() => {
                                  applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDefaults(entry);
                                }}
                                type="button"
                              >
                                Use defaults
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">No moderation governance meta-policies saved yet.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <div className="market-data-provenance-history-head">
                  <strong>Moderation governance approval queue</strong>
                  <p>
                    Stage selected moderation governance policies, preview the exact policy diffs,
                    then approve and apply the change set.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.action}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                          ...current,
                          action: event.target.value,
                        }));
                      }}
                    >
                      <option value="update">Update</option>
                      <option value="delete">Delete</option>
                      <option value="restore">Restore</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Reusable meta-policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.meta_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                          ...current,
                          meta_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>Inline policy patch</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-meta-policy-option-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Approval/apply note</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                          ...current,
                          note: event.target.value,
                        }));
                      }}
                      placeholder="required when the meta-policy gates approval on notes"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.note}
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId !== null
                    }
                    onClick={() => {
                      void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaSelection();
                    }}
                    type="button"
                  >
                    Stage selected policies
                  </button>
                  <label className="run-form-field">
                    <span>Queue state</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.queue_state}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                          ...current,
                          queue_state: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All states</option>
                      <option value="pending_approval">Pending approval</option>
                      <option value="ready_to_apply">Ready to apply</option>
                      <option value="completed">Completed</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Meta-policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.meta_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                          ...current,
                          meta_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All meta-policies</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.available_filters.meta_policies ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-meta-plan-policy-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <span className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.completed_count ?? 0} completed
                  </span>
                </div>
                {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError ? (
                  <p className="market-data-workflow-feedback">
                    Moderation governance approval queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError}
                  </p>
                ) : null}
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Preview</th>
                      <th>Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-governance-meta-plan-${entry.plan_id}`}>
                          <td>
                            <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.action)} · {entry.meta_policy_name ?? "Inline defaults"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                            </p>
                            {entry.guidance ? (
                              <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{entry.preview_count} preview item(s)</strong>
                            {entry.preview_items.slice(0, 4).map((preview) => (
                              <div key={`provider-scheduler-search-moderation-governance-meta-preview-${entry.plan_id}-${preview.governance_policy_id}`}>
                                <p className="run-lineage-symbol-copy">
                                  {preview.governance_policy_name} · {formatWorkflowToken(preview.outcome)}
                                  {preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                                  {preview.message ? ` · ${preview.message}` : ""}
                                </p>
                                {Object.entries(preview.field_diffs).slice(0, 2).map(([field, diff]) => (
                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-governance-meta-diff-${entry.plan_id}-${preview.governance_policy_id}-${field}`}>
                                    {field}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.before)} → {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.after)}
                                  </p>
                                ))}
                              </div>
                            ))}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                            </p>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "pending_approval"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "ready_to_apply"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                                }}
                                type="button"
                              >
                                Apply
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">No moderation governance meta-plans match the current filter.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <div className="market-data-provenance-history-head">
                  <strong>Moderation catalog governance queue</strong>
                  <p>
                    Stage selected moderation policy catalogs, preview the exact catalog diffs,
                    then approve and apply the change set.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.action}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                          ...current,
                          action: event.target.value,
                        }));
                      }}
                    >
                      <option value="update">Update</option>
                      <option value="delete">Delete</option>
                      <option value="restore">Restore</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.governance_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                          ...current,
                          governance_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>No reusable policy</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-policy-option-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Approval/apply note</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                          ...current,
                          note: event.target.value,
                        }));
                      }}
                      placeholder="required when the governance policy gates approval on notes"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.note}
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId !== null
                    }
                    onClick={() => {
                      void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceSelection();
                    }}
                    type="button"
                  >
                    Stage selected catalogs
                  </button>
                  <label className="run-form-field">
                    <span>Queue state</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.queue_state}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                          ...current,
                          queue_state: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All states</option>
                      <option value="pending_approval">Pending approval</option>
                      <option value="ready_to_apply">Ready to apply</option>
                      <option value="completed">Completed</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.governance_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                          ...current,
                          governance_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All policies</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.available_filters.governance_policies ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-queue-policy-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <span className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.completed_count ?? 0} completed
                  </span>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Preview</th>
                      <th>Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernancePlans.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-catalog-governance-plan-${entry.plan_id}`}>
                          <td>
                            <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.action)} · {entry.governance_policy_name ?? "No policy"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                            </p>
                            {entry.guidance ? (
                              <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{entry.preview_count} preview item(s)</strong>
                            {entry.preview_items.slice(0, 4).map((preview) => (
                              <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-catalog-governance-preview-${entry.plan_id}-${preview.catalog_id}`}>
                                {preview.catalog_name} · {formatWorkflowToken(preview.outcome)}{preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                                {preview.message ? ` · ${preview.message}` : ""}
                              </p>
                            ))}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                            </p>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "pending_approval"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "ready_to_apply"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Apply
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">No moderation catalog governance plans match the current filter.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <div className="market-data-provenance-history-head">
                  <strong>Scheduler moderation approval queue</strong>
                  <p>
                    Stage selected feedback, review the plan preview, then approve and apply it
                    as a governed moderation batch.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Stage policy catalog</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationStageDraft.policy_catalog_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                          ...current,
                          policy_catalog_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>No catalog</option>
                      {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-stage-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Fallback outcome</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationStageDraft.moderation_status}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                          ...current,
                          moderation_status: event.target.value,
                        }));
                      }}
                    >
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="pending">Pending</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Approval/apply note</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                          ...current,
                          note: event.target.value,
                        }));
                      }}
                      placeholder="required by policy catalogs that gate approval on notes"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationStageDraft.note}
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                      || providerProvenanceSchedulerSearchModerationPlanPendingId !== null
                    }
                    onClick={() => {
                      void stageProviderProvenanceSchedulerSearchModerationSelection();
                    }}
                    type="button"
                  >
                    Stage selected feedback
                  </button>
                  <label className="run-form-field">
                    <span>Queue state</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationQueueFilter.queue_state}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                          ...current,
                          queue_state: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All states</option>
                      <option value="pending_approval">Pending approval</option>
                      <option value="ready_to_apply">Ready to apply</option>
                      <option value="completed">Completed</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Policy catalog</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationQueueFilter.policy_catalog_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                          ...current,
                          policy_catalog_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All catalogs</option>
                      {(providerProvenanceSchedulerSearchModerationPlans?.available_filters.policy_catalogs ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-queue-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <span className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerSearchModerationPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationPlans?.summary.completed_count ?? 0} completed
                  </span>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Preview</th>
                      <th>Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationPlans?.items.length ? (
                      providerProvenanceSchedulerSearchModerationPlans.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-plan-${entry.plan_id}`}>
                          <td>
                            <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                            <p className="run-lineage-symbol-copy">
                              {entry.policy_catalog_name ?? "No catalog"} · {formatWorkflowToken(entry.proposed_moderation_status)}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Eligible {entry.feedback_ids.length}/{entry.requested_feedback_ids.length} · minimum score {entry.minimum_score}
                            </p>
                          </td>
                          <td>
                            <strong>{entry.preview_count} preview item(s)</strong>
                            {entry.preview_items.slice(0, 4).map((preview) => (
                              <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-preview-${entry.plan_id}-${preview.feedback_id}`}>
                                {preview.occurrence_id} · {formatWorkflowToken(preview.current_moderation_status)} → {formatWorkflowToken(preview.proposed_moderation_status)} · score {preview.score} · {preview.eligible ? "eligible" : "skipped"}
                                {preview.reason_tags.length ? ` · ${preview.reason_tags.join(" · ")}` : ""}
                              </p>
                            ))}
                            {entry.missing_feedback_ids.length ? (
                              <p className="run-lineage-symbol-copy">
                                Missing {entry.missing_feedback_ids.join(" · ")}
                              </p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                            </p>
                            {entry.approval_note ? (
                              <p className="run-lineage-symbol-copy">{entry.approval_note}</p>
                            ) : null}
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "pending_approval"
                                  || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void approveProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "ready_to_apply"
                                  || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void applyProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Apply
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">
                            No staged scheduler moderation plans match the current queue filter.
                          </p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </>
            ) : null}
            {providerProvenanceSchedulerSearchDashboardLoading ? (
              <p className="empty-state">Loading scheduler search dashboard…</p>
            ) : null}
            {providerProvenanceSchedulerSearchDashboardError ? (
              <p className="market-data-workflow-feedback">
                Scheduler search dashboard failed: {providerProvenanceSchedulerSearchDashboardError}
              </p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading
            || providerProvenanceSchedulerSearchModerationPlansLoading
            || providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading
            || providerProvenanceSchedulerSearchModerationCatalogGovernancePlansLoading ? (
              <p className="empty-state">Loading scheduler moderation governance…</p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationPolicyCatalogsError ? (
              <p className="market-data-workflow-feedback">
                Scheduler moderation policy catalogs failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogsError}
              </p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError ? (
              <p className="market-data-workflow-feedback">
                Scheduler moderation catalog governance policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError}
              </p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError ? (
              <p className="market-data-workflow-feedback">
                Scheduler moderation catalog governance queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError}
              </p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationPlansError ? (
              <p className="market-data-workflow-feedback">
                Scheduler moderation approval queue failed: {providerProvenanceSchedulerSearchModerationPlansError}
              </p>
            ) : null}
    </>
  );
}
