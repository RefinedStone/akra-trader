// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateRegistrySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Shift-lead cleanup"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="high-signal delete workflow"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.description}
          />
        </label>
        <label>
          <span>Item scope</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                item_type_scope:
                  event.target.value === "template"
                  || event.target.value === "registry"
                  || event.target.value === "stitched_report_view"
                  || event.target.value === "stitched_report_governance_registry"
                    ? event.target.value
                    : "any",
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.item_type_scope}
          >
            <option value="any">Any item</option>
            <option value="template">Templates</option>
            <option value="registry">Registry</option>
            <option value="stitched_report_view">Stitched report views</option>
            <option value="stitched_report_governance_registry">Stitched governance registries</option>
          </select>
        </label>
        <label>
          <span>Action scope</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                action_scope:
                  event.target.value === "delete"
                  || event.target.value === "restore"
                  || event.target.value === "update"
                    ? event.target.value
                    : "any",
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.action_scope}
          >
            <option value="any">Any action</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
            <option value="restore">Restore</option>
          </select>
        </label>
        <label>
          <span>Approval lane</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                approval_lane: event.target.value,
              }))
            }
            placeholder="shift_lead"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.approval_lane}
          />
        </label>
        <label>
          <span>Priority</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                approval_priority:
                  event.target.value === "low"
                  || event.target.value === "high"
                  || event.target.value === "critical"
                    ? event.target.value
                    : "normal",
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.approval_priority}
          >
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </label>
        <label>
          <span>Guidance</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft((current) => ({
                ...current,
                guidance: event.target.value,
              }))
            }
            placeholder="Review with shift lead before apply."
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft.guidance}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId
                ? "Save revision"
                : "Save policy"}
            </button>
            {editingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft();
                }}
                type="button"
              >
                Cancel
              </button>
            ) : null}
          </div>
        </label>
      </div>
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Policy catalog workflow</strong>
            <p>Bundle selected governance policy templates into a reusable catalog and reapply its queue/default-policy context later.</p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Selection</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelections}
                  type="button"
                >
                  {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds.length === providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length
                    ? "Clear all"
                    : "Select all"}
                </button>
              </div>
              <p className="run-lineage-symbol-copy">
                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries.length} template(s) selected
              </p>
            </label>
            <label>
              <span>Catalog name</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Shift lead governance catalog"
                type="text"
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft.name}
              />
            </label>
            <label>
              <span>Description</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
                placeholder="High-signal batch policies"
                type="text"
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft.description}
              />
            </label>
            <label>
              <span>Default template</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft((current) => ({
                    ...current,
                    default_policy_template_id: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft.default_policy_template_id}
              >
                <option value="">First selected template</option>
                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries.map((entry) => (
                  <option key={entry.policy_template_id} value={entry.policy_template_id}>
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
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries.length}
                  onClick={() => {
                    void saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog();
                  }}
                  type="button"
                >
                  {editingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId
                    ? "Update catalog"
                    : "Save catalog"}
                </button>
                {editingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId ? (
                  <button
                    className="ghost-button"
                    onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft}
                    type="button"
                  >
                    Cancel edit
                  </button>
                ) : (
                  <button
                    className="ghost-button"
                    onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft}
                    type="button"
                  >
                    Reset
                  </button>
                )}
              </div>
            </label>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesLoading ? (
        <p className="empty-state">Loading governance policy templates…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesError ? (
        <p className="market-data-workflow-feedback">
          Governance policy template registry load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all governance policy templates"
                  checked={
                    providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length > 0
                    && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds.length === providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelections}
                  type="checkbox"
                />
              </th>
              <th>Template</th>
              <th>Scope</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
              <tr key={entry.policy_template_id}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select governance policy template ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIdSet.has(entry.policy_template_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelection(entry.policy_template_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">
                    {entry.description || "No description."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.guidance || "No guidance."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s) · updated {formatTimestamp(entry.updated_at)}
                  </p>
                </td>
                <td>
                  <strong>
                    {formatWorkflowToken(entry.item_type_scope)} · {formatWorkflowToken(entry.action_scope)}
                  </strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        if (entry.status !== "active") {
                          return;
                        }
                        if (
                          providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                            entry.item_type_scope,
                            "template",
                          )
                        ) {
                          setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId(entry.policy_template_id);
                        }
                        if (
                          providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                            entry.item_type_scope,
                            "registry",
                          )
                        ) {
                          setProviderProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId(entry.policy_template_id);
                        }
                        if (
                          providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                            entry.item_type_scope,
                            "stitched_report_view",
                          )
                        ) {
                          setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId(entry.policy_template_id);
                        }
                        if (
                          providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                            entry.item_type_scope,
                            "stitched_report_governance_registry",
                          )
                        ) {
                          setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId(
                            entry.policy_template_id,
                          );
                        }
                      }}
                      disabled={entry.status !== "active"}
                      type="button"
                    >
                      Use defaults
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        editProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(entry);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void removeProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(entry);
                      }}
                      type="button"
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory(
                          entry.policy_template_id,
                        );
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId === entry.policy_template_id
                        && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory
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
        <p className="empty-state">No governance policy templates saved yet.</p>
      )}
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Policy template revision history</strong>
          <p>Review policy snapshots, stage an older revision into the editor, or restore it as the active template.</p>
        </div>
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryLoading ? (
          <p className="empty-state">Loading policy template revisions…</p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryError ? (
          <p className="market-data-workflow-feedback">
            Policy template revision history failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryError}
          </p>
        ) : null}
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Revision</th>
                <th>Scope</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory.history.map((entry) => (
                <tr key={entry.revision_id}>
                  <td>
                    <strong>{entry.revision_id}</strong>
                    <p className="run-lineage-symbol-copy">
                      {entry.name}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {entry.reason}
                    </p>
                  </td>
                  <td>
                    <strong>
                      {formatWorkflowToken(entry.item_type_scope)} · {formatWorkflowToken(entry.action_scope)}
                    </strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {entry.guidance || "No guidance."}
                    </p>
                  </td>
                  <td>
                    <div className="market-data-provenance-history-actions">
                      <button
                        className="ghost-button"
                        onClick={() => {
                          setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId(
                            entry.policy_template_id,
                          );
                          setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateDraft({
                            name: entry.name,
                            description: entry.description,
                            item_type_scope:
                              entry.item_type_scope === "template"
                              || entry.item_type_scope === "registry"
                              || entry.item_type_scope === "stitched_report_view"
                              || entry.item_type_scope === "stitched_report_governance_registry"
                                ? entry.item_type_scope
                                : "any",
                            action_scope:
                              entry.action_scope === "delete"
                              || entry.action_scope === "restore"
                              || entry.action_scope === "update"
                                ? entry.action_scope
                                : "any",
                            approval_lane: entry.approval_lane,
                            approval_priority:
                              entry.approval_priority === "low"
                              || entry.approval_priority === "high"
                              || entry.approval_priority === "critical"
                                ? entry.approval_priority
                                : "normal",
                            guidance: entry.guidance ?? "",
                          });
                          setProviderProvenanceWorkspaceFeedback(
                            `Policy template revision ${entry.revision_id} staged in the editor.`,
                          );
                        }}
                        type="button"
                      >
                        Stage draft
                      </button>
                      <button
                        className="ghost-button"
                        onClick={() => {
                          void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistoryRevision(
                            entry,
                          );
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
        ) : (
          <p className="empty-state">Select a policy template row and open Versions to inspect revisions.</p>
        )}
      </div>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Policy template team audit</strong>
          <p>Filter shared audit events by template, action, or actor to review who changed governance defaults.</p>
        </div>
        <div className="filter-bar">
          <label>
            <span>Template</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                  ...current,
                  policy_template_id: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.policy_template_id}
            >
              <option value="">All templates</option>
              {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
                <option key={entry.policy_template_id} value={entry.policy_template_id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Action</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                  ...current,
                  action: event.target.value,
                }))
              }
              value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.action}
            >
              <option value={ALL_FILTER_VALUE}>All actions</option>
              <option value="created">Created</option>
              <option value="updated">Updated</option>
              <option value="deleted">Deleted</option>
              <option value="restored">Restored</option>
            </select>
          </label>
          <label>
            <span>Actor</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                  ...current,
                  actor_tab_id: event.target.value,
                }))
              }
              placeholder="tab_ops"
              type="text"
              value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.actor_tab_id}
            />
          </label>
          <label>
            <span>Search</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
              placeholder="shift lead, restore"
              type="search"
              value={providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditFilter.search}
            />
          </label>
          <label>
            <span>Action</span>
            <button
              className="ghost-button"
              onClick={() => {
                void loadProviderProvenanceWorkspaceRegistry();
              }}
              type="button"
            >
              Refresh audit
            </button>
          </label>
        </div>
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsLoading ? (
          <p className="empty-state">Loading policy template audit trail…</p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError ? (
          <p className="market-data-workflow-feedback">
            Policy template audit load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError}
          </p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Audit</th>
                <th>Template</th>
                <th>Actor</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits.map((entry) => (
                <tr key={entry.audit_id}>
                  <td>
                    <strong>{formatWorkflowToken(entry.action)}</strong>
                    <p className="run-lineage-symbol-copy">
                      {entry.detail}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {formatTimestamp(entry.recorded_at)}
                    </p>
                  </td>
                  <td>
                    <strong>{entry.name}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.item_type_scope)} / {formatWorkflowToken(entry.action_scope)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
                    </p>
                  </td>
                  <td>
                    <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "system"}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {entry.reason}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty-state">No policy template audit records match the current filter.</p>
        )}
      </div>
    </>
  );
}
