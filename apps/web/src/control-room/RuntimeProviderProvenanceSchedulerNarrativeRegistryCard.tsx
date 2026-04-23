// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryCard({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Scheduler narrative registry</strong>
        <p>Store a named shared review board for occurrence narratives with an optional template link.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Lag recovery board"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="shared scheduler occurrence board"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryDraft.description}
          />
        </label>
        <label>
          <span>Template</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                ...current,
                template_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryDraft.template_id}
          >
            <option value="">No template link</option>
            {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
              <option key={entry.template_id} value={entry.template_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveCurrentProviderProvenanceSchedulerNarrativeRegistryEntry();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerNarrativeRegistryId ? "Save changes" : "Save registry"}
            </button>
            {editingProviderProvenanceSchedulerNarrativeRegistryId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerNarrativeRegistryDraft();
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
        </label>
      </div>
      {providerProvenanceSchedulerNarrativeRegistryEntries.length ? (
        <div className="provider-provenance-governance-bar">
          <div className="provider-provenance-governance-summary">
            <strong>
              {selectedProviderProvenanceSchedulerNarrativeRegistryIds.length} selected
            </strong>
            <span>
              {selectedProviderProvenanceSchedulerNarrativeRegistryEntries.filter((entry) => entry.status === "active").length} active ·{" "}
              {selectedProviderProvenanceSchedulerNarrativeRegistryEntries.filter((entry) => entry.status === "deleted").length} deleted
            </span>
          </div>
          <div className="market-data-provenance-history-actions">
            <label>
              <span>Policy</span>
              <select
                onChange={(event) => {
                  setProviderProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId(event.target.value);
                }}
                value={providerProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId}
              >
                <option value="">No policy template</option>
                {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                  .filter((entry) => entry.item_type_scope === "any" || entry.item_type_scope === "registry")
                  .map((entry) => (
                    <option key={entry.policy_template_id} value={entry.policy_template_id}>
                      {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                    </option>
                  ))}
              </select>
            </label>
            <button
              className="ghost-button"
              onClick={toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections}
              type="button"
            >
              {selectedProviderProvenanceSchedulerNarrativeRegistryIds.length === providerProvenanceSchedulerNarrativeRegistryEntries.length
                ? "Clear all"
                : "Select all"}
            </button>
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeRegistryIds.length || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance("delete");
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeRegistryBulkAction === "delete"
                ? "Previewing…"
                : "Preview delete"}
            </button>
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeRegistryIds.length || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance("restore");
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeRegistryBulkAction === "restore"
                ? "Previewing…"
                : "Preview restore"}
            </button>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerNarrativeRegistryEntries.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Advanced bulk edits</strong>
            <p>Preview metadata, query, template-link, or board-layout patches, then approve and apply them with rollback planning.</p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Name prefix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }))
                }
                placeholder="Ops / "
                type="text"
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.name_prefix}
              />
            </label>
            <label>
              <span>Name suffix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }))
                }
                placeholder=" / board"
                type="text"
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.name_suffix}
              />
            </label>
            <label>
              <span>Description append</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }))
                }
                placeholder="shared governance update"
                type="text"
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.description_append}
              />
            </label>
            <label>
              <span>Category</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_category: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.scheduler_alert_category}
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
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_status: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.scheduler_alert_status}
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
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
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
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.scheduler_alert_narrative_facet}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="all_occurrences">all occurrences</option>
                <option value="resolved_narratives">resolved narratives</option>
                <option value="post_resolution_recovery">post-resolution recovery</option>
                <option value="recurring_occurrences">recurring occurrences</option>
              </select>
            </label>
            <label>
              <span>Template link</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    template_id: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.template_id}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE}>Clear link</option>
                {providerProvenanceSchedulerNarrativeTemplates
                  .filter((entry) => entry.status === "active")
                  .map((entry) => (
                    <option key={entry.template_id} value={entry.template_id}>
                      {entry.name}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              <span>Rollups</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    show_rollups:
                      event.target.value === "enable" || event.target.value === "disable"
                        ? event.target.value
                        : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.show_rollups}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="enable">Enable</option>
                <option value="disable">Disable</option>
              </select>
            </label>
            <label>
              <span>Time series</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    show_time_series:
                      event.target.value === "enable" || event.target.value === "disable"
                        ? event.target.value
                        : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.show_time_series}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="enable">Enable</option>
                <option value="disable">Disable</option>
              </select>
            </label>
            <label>
              <span>Recent exports</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    show_recent_exports:
                      event.target.value === "enable" || event.target.value === "disable"
                        ? event.target.value
                        : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.show_recent_exports}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="enable">Enable</option>
                <option value="disable">Disable</option>
              </select>
            </label>
            <label>
              <span>Window days</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    window_days: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.window_days}
              />
            </label>
            <label>
              <span>Result limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                    ...current,
                    result_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.result_limit}
              />
            </label>
            <label>
              <span>Action</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeRegistryIds.length || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance("update");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeRegistryBulkAction === "update"
                    ? "Previewing…"
                    : "Preview bulk edit"}
                </button>
              </div>
            </label>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerNarrativeRegistryEntriesLoading ? (
        <p className="empty-state">Loading scheduler narrative registry…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeRegistryEntriesError ? (
        <p className="market-data-workflow-feedback">
          Scheduler narrative registry load failed: {providerProvenanceSchedulerNarrativeRegistryEntriesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeRegistryEntries.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all scheduler narrative registry entries"
                  checked={
                    providerProvenanceSchedulerNarrativeRegistryEntries.length > 0
                    && selectedProviderProvenanceSchedulerNarrativeRegistryIds.length === providerProvenanceSchedulerNarrativeRegistryEntries.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections}
                  type="checkbox"
                />
              </th>
              <th>Registry</th>
              <th>Linked lens</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeRegistryEntries.map((entry) => (
              <tr key={entry.registry_id}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select scheduler narrative registry ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerNarrativeRegistryIdSet.has(entry.registry_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeRegistrySelection(entry.registry_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.filter_summary}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <strong>{providerProvenanceSchedulerNarrativeTemplateNameMap.get(entry.template_id ?? "") ?? "No template link"}</strong>
                  <p className="run-lineage-symbol-copy">
                    Highlight {entry.layout.highlight_panel} · {entry.focus.symbol ?? "all symbols"} · {entry.focus.timeframe ?? "all windows"}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s) · updated {formatTimestamp(entry.updated_at)}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        setProviderProvenanceSchedulerNarrativeRegistryDraft((current) => ({
                          ...current,
                          template_id: entry.template_id ?? "",
                        }));
                        void applyProviderProvenanceWorkspaceQuery(entry, {
                          includeLayout: true,
                          feedbackLabel: `Narrative registry ${entry.name}`,
                        });
                      }}
                      type="button"
                    >
                      Apply
                    </button>
                    <button
                      className="ghost-button"
                      disabled={providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                      onClick={() => {
                        void editProviderProvenanceSchedulerNarrativeRegistryEntry(entry);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active" || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                      onClick={() => {
                        void removeProviderProvenanceSchedulerNarrativeRegistry(entry);
                      }}
                      type="button"
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      disabled={providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
                      onClick={() => {
                        void toggleProviderProvenanceSchedulerNarrativeRegistryHistory(entry.registry_id);
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerNarrativeRegistryId === entry.registry_id
                        && selectedProviderProvenanceSchedulerNarrativeRegistryHistory
                        ? "Hide versions"
                        : "Versions"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No scheduler narrative registry entries saved yet.</p>
      )}
      {selectedProviderProvenanceSchedulerNarrativeRegistryId ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Registry revision history</strong>
            <p>Review saved board revisions, apply them to the workbench, or restore them as the active shared scheduler board.</p>
          </div>
          {providerProvenanceSchedulerNarrativeRegistryHistoryLoading ? (
            <p className="empty-state">Loading registry revisions…</p>
          ) : null}
          {providerProvenanceSchedulerNarrativeRegistryHistoryError ? (
            <p className="market-data-workflow-feedback">
              Registry revision history failed: {providerProvenanceSchedulerNarrativeRegistryHistoryError}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeRegistryHistory ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Snapshot</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {selectedProviderProvenanceSchedulerNarrativeRegistryHistory.history.map((entry) => (
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
                        {providerProvenanceSchedulerNarrativeTemplateNameMap.get(entry.template_id ?? "") ?? "No template link"} · highlight {entry.layout.highlight_panel}
                      </p>
                      <p className="run-lineage-symbol-copy">{entry.reason}</p>
                    </td>
                    <td>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          onClick={() => {
                            void applyProviderProvenanceWorkspaceQuery(entry, {
                              includeLayout: true,
                              feedbackLabel: `Registry revision ${entry.revision_id}`,
                            });
                          }}
                          type="button"
                        >
                          Apply snapshot
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            void restoreProviderProvenanceSchedulerNarrativeRegistryHistoryRevision(entry);
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
    </div>
  );
}
