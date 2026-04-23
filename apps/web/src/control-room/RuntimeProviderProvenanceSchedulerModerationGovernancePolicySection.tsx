// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationGovernancePolicySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
