// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Scheduler narrative templates</strong>
        <p>Save reusable occurrence lenses that only carry the scheduler narrative query state.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Resolved lag recovery"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="resolved scheduler narrative lens"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateDraft.description}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveCurrentProviderProvenanceSchedulerNarrativeTemplate();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerNarrativeTemplateId ? "Save changes" : "Save template"}
            </button>
            {editingProviderProvenanceSchedulerNarrativeTemplateId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerNarrativeTemplateDraft();
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
        </label>
      </div>
      {providerProvenanceSchedulerNarrativeTemplates.length ? (
        <div className="provider-provenance-governance-bar">
          <div className="provider-provenance-governance-summary">
            <strong>
              {selectedProviderProvenanceSchedulerNarrativeTemplateIds.length} selected
            </strong>
            <span>
              {selectedProviderProvenanceSchedulerNarrativeTemplateEntries.filter((entry) => entry.status === "active").length} active ·{" "}
              {selectedProviderProvenanceSchedulerNarrativeTemplateEntries.filter((entry) => entry.status === "deleted").length} deleted
            </span>
          </div>
          <div className="market-data-provenance-history-actions">
            <label>
              <span>Policy</span>
              <select
                onChange={(event) => {
                  setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId(event.target.value);
                }}
                value={providerProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId}
              >
                <option value="">No policy template</option>
                {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                  .filter((entry) => entry.item_type_scope === "any" || entry.item_type_scope === "template")
                  .map((entry) => (
                    <option key={entry.policy_template_id} value={entry.policy_template_id}>
                      {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                    </option>
                  ))}
              </select>
            </label>
            <button
              className="ghost-button"
              onClick={toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections}
              type="button"
            >
              {selectedProviderProvenanceSchedulerNarrativeTemplateIds.length === providerProvenanceSchedulerNarrativeTemplates.length
                ? "Clear all"
                : "Select all"}
            </button>
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeTemplateIds.length || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance("delete");
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeTemplateBulkAction === "delete"
                ? "Previewing…"
                : "Preview delete"}
            </button>
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeTemplateIds.length || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance("restore");
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeTemplateBulkAction === "restore"
                ? "Previewing…"
                : "Preview restore"}
            </button>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplates.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Advanced bulk edits</strong>
            <p>Preview metadata or scheduler-lens patches, then approve and apply them with rollback planning.</p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Name prefix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }))
                }
                placeholder="Ops / "
                type="text"
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.name_prefix}
              />
            </label>
            <label>
              <span>Name suffix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }))
                }
                placeholder=" / v2"
                type="text"
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.name_suffix}
              />
            </label>
            <label>
              <span>Description append</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }))
                }
                placeholder="reviewed in shift handoff"
                type="text"
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.description_append}
              />
            </label>
            <label>
              <span>Category</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_category: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.scheduler_alert_category}
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
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_status: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.scheduler_alert_status}
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
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
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
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.scheduler_alert_narrative_facet}
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
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    window_days: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.window_days}
              />
            </label>
            <label>
              <span>Result limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                    ...current,
                    result_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.result_limit}
              />
            </label>
            <label>
              <span>Action</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeTemplateIds.length || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance("update");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeTemplateBulkAction === "update"
                    ? "Previewing…"
                    : "Preview bulk edit"}
                </button>
              </div>
            </label>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplatesLoading ? (
        <p className="empty-state">Loading scheduler narrative templates…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplatesError ? (
        <p className="market-data-workflow-feedback">
          Scheduler narrative template registry load failed: {providerProvenanceSchedulerNarrativeTemplatesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeTemplates.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all scheduler narrative templates"
                  checked={
                    providerProvenanceSchedulerNarrativeTemplates.length > 0
                    && selectedProviderProvenanceSchedulerNarrativeTemplateIds.length === providerProvenanceSchedulerNarrativeTemplates.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerNarrativeTemplateSelections}
                  type="checkbox"
                />
              </th>
              <th>Template</th>
              <th>Lens</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
              <tr key={entry.template_id}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select scheduler narrative template ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerNarrativeTemplateIdSet.has(entry.template_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeTemplateSelection(entry.template_id);
                    }}
                    type="checkbox"
                  />
                </td>
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
                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Updated {formatTimestamp(entry.updated_at)}{entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
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
                          template_id: entry.template_id,
                        }));
                        void applyProviderProvenanceWorkspaceQuery(entry, {
                          includeLayout: false,
                          forceSchedulerHighlight: true,
                          feedbackLabel: `Scheduler template ${entry.name}`,
                        });
                      }}
                      type="button"
                    >
                      Apply
                    </button>
                    <button
                      className="ghost-button"
                      disabled={providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                      onClick={() => {
                        void editProviderProvenanceSchedulerNarrativeTemplate(entry);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active" || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                      onClick={() => {
                        void removeProviderProvenanceSchedulerNarrativeTemplate(entry);
                      }}
                      type="button"
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      disabled={providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
                      onClick={() => {
                        void toggleProviderProvenanceSchedulerNarrativeTemplateHistory(entry.template_id);
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerNarrativeTemplateId === entry.template_id
                        && selectedProviderProvenanceSchedulerNarrativeTemplateHistory
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
        <p className="empty-state">No scheduler narrative templates saved yet.</p>
      )}
      {selectedProviderProvenanceSchedulerNarrativeTemplateId ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Template revision history</strong>
            <p>Inspect immutable snapshots, apply them to the workbench, or restore them as the active template.</p>
          </div>
          {providerProvenanceSchedulerNarrativeTemplateHistoryLoading ? (
            <p className="empty-state">Loading template revisions…</p>
          ) : null}
          {providerProvenanceSchedulerNarrativeTemplateHistoryError ? (
            <p className="market-data-workflow-feedback">
              Template revision history failed: {providerProvenanceSchedulerNarrativeTemplateHistoryError}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeTemplateHistory ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Snapshot</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {selectedProviderProvenanceSchedulerNarrativeTemplateHistory.history.map((entry) => (
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
                              feedbackLabel: `Template revision ${entry.revision_id}`,
                            });
                          }}
                          type="button"
                        >
                          Apply snapshot
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            void restoreProviderProvenanceSchedulerNarrativeTemplateHistoryRevision(entry);
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
