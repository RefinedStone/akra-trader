// @ts-nocheck
import { RuntimeProviderProvenanceScheduledReportsCard } from "./RuntimeProviderProvenanceScheduledReportsCard";

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
                                <div className="provider-provenance-workspace-card">
                                  <div className="market-data-provenance-history-head">
                                    <strong>Governance policy templates</strong>
                                    <p>Save reusable approval-lane defaults, manage revisions, and review the shared audit trail for policy edits.</p>
                                  </div>
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
                                  <div className="market-data-provenance-shared-history">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Governance policy catalogs</strong>
                                      <p>Reuse named policy bundles, review catalog revisions, and bulk-govern shared queue defaults without editing each catalog one by one.</p>
                                    </div>
                                    {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length ? (
                                      <div className="filter-bar">
                                        <label>
                                          <span>Selection</span>
                                          <button
                                            className="ghost-button"
                                            onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelections}
                                            type="button"
                                          >
                                            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds.length
                                              === providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length
                                              ? "Clear all"
                                              : "Select all"}
                                          </button>
                                          <p className="run-lineage-symbol-copy">
                                            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length} catalog(s) selected
                                          </p>
                                        </label>
                                        <label>
                                          <span>Name prefix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }))
                                            }
                                            placeholder="Shift "
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.name_prefix}
                                          />
                                        </label>
                                        <label>
                                          <span>Name suffix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }))
                                            }
                                            placeholder=" / archived"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.name_suffix}
                                          />
                                        </label>
                                        <label>
                                          <span>Description append</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                description_append: event.target.value,
                                              }))
                                            }
                                            placeholder="requires desk review"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.description_append}
                                          />
                                        </label>
                                        <label>
                                          <span>Default template</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                                                ...current,
                                                default_policy_template_id: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.default_policy_template_id}
                                          >
                                            <option value="">Keep current default</option>
                                            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                                              .filter((entry) => entry.status === "active")
                                              .map((entry) => (
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
                                              disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
                                              onClick={() => {
                                                void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("delete");
                                              }}
                                              type="button"
                                            >
                                              {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "delete"
                                                ? "Deleting…"
                                                : "Delete selected"}
                                            </button>
                                            <button
                                              className="ghost-button"
                                              disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
                                              onClick={() => {
                                                void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("restore");
                                              }}
                                              type="button"
                                            >
                                              {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "restore"
                                                ? "Restoring…"
                                                : "Restore selected"}
                                            </button>
                                            <button
                                              className="ghost-button"
                                              disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
                                              onClick={() => {
                                                void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("update");
                                              }}
                                              type="button"
                                            >
                                              {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "update"
                                                ? "Updating…"
                                                : "Apply bulk edit"}
                                            </button>
                                          </div>
                                        </label>
                                      </div>
                                    ) : null}
                                    {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsLoading ? (
                                      <p className="empty-state">Loading governance policy catalogs…</p>
                                    ) : null}
                                    {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError ? (
                                      <p className="market-data-workflow-feedback">
                                        Governance policy catalog load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError}
                                      </p>
                                    ) : null}
                                    {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length ? (
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th aria-label="Select catalog">Sel</th>
                                            <th>Catalog</th>
                                            <th>Defaults</th>
                                            <th>Action</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((catalog) => (
                                            <tr key={catalog.catalog_id}>
                                              <td>
                                                <input
                                                  checked={selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet.has(catalog.catalog_id)}
                                                  onChange={() => {
                                                    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelection(catalog.catalog_id);
                                                  }}
                                                  type="checkbox"
                                                />
                                              </td>
                                              <td>
                                                <strong>{catalog.name}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.description || "No description."}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.policy_template_names.join(", ") || "No linked templates."}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.status)} · {catalog.revision_count} revision(s) · updated {formatTimestamp(catalog.updated_at)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(catalog.hierarchy_steps)}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>{catalog.default_policy_template_name ?? "No default template"}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {catalog.created_by_tab_label ?? catalog.created_by_tab_id ?? "unknown tab"}
                                                </p>
                                              </td>
                                              <td>
                                                <div className="market-data-provenance-history-actions">
                                                  <button
                                                    className="ghost-button"
                                                    disabled={catalog.status !== "active"}
                                                    onClick={() => {
                                                      applyProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Apply catalog
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={catalog.status !== "active"}
                                                    onClick={() => {
                                                      void captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyForCatalog(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Capture hierarchy
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
                                                    onClick={() => {
                                                      void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Stage queue
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Edit
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void removeProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
                                                    }}
                                                    type="button"
                                                  >
                                                    Delete
                                                  </button>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory(
                                                        catalog.catalog_id,
                                                      );
                                                    }}
                                                    type="button"
                                                  >
                                                    {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId === catalog.catalog_id
                                                      && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory
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
                                      <p className="empty-state">No governance policy catalogs saved yet.</p>
                                    )}
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Catalog revision history</strong>
                                        <p>Stage a previous linked-template snapshot or restore it as the active policy catalog.</p>
                                      </div>
                                      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryLoading ? (
                                        <p className="empty-state">Loading policy catalog revisions…</p>
                                      ) : null}
                                      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError ? (
                                        <p className="market-data-workflow-feedback">
                                          Policy catalog revision history failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Revision</th>
                                              <th>Defaults</th>
                                              <th>Action</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory.history.map((entry) => (
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
                                                  <strong>{entry.default_policy_template_name ?? "No default template"}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.policy_template_names.join(", ") || "No linked templates."}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.approval_lane)} / {formatWorkflowToken(entry.approval_priority)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(entry.hierarchy_steps)}
                                                  </p>
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId(
                                                          entry.catalog_id,
                                                        );
                                                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft({
                                                          name: entry.name,
                                                          description: entry.description,
                                                          default_policy_template_id: entry.default_policy_template_id ?? "",
                                                        });
                                                        setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds(
                                                          entry.policy_template_ids,
                                                        );
                                                        setProviderProvenanceWorkspaceFeedback(
                                                          `Policy catalog revision ${entry.revision_id} staged in the editor.`,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Stage draft
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryRevision(
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
                                        <p className="empty-state">Select a policy catalog row and open Versions to inspect revisions.</p>
                                      )}
                                    </div>
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Catalog hierarchy steps</strong>
                                        <p>Edit reusable hierarchy steps, bulk-govern selected steps, and restore an older step snapshot without restoring the whole catalog.</p>
                                      </div>
                                      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog ? (
                                        <>
                                          <div className="filter-bar">
                                            <label>
                                              <span>Selection</span>
                                              <button
                                                className="ghost-button"
                                                disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length}
                                                onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelections}
                                                type="button"
                                              >
                                                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length
                                                  === selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length
                                                  && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length
                                                  ? "Clear all"
                                                  : "Select all"}
                                              </button>
                                            </label>
                                            <label>
                                              <span>Bulk name prefix</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    name_prefix: event.target.value,
                                                  }))
                                                }
                                                placeholder="Reviewed / "
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.name_prefix}
                                              />
                                            </label>
                                            <label>
                                              <span>Bulk name suffix</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    name_suffix: event.target.value,
                                                  }))
                                                }
                                                placeholder=" / approved"
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.name_suffix}
                                              />
                                            </label>
                                            <label>
                                              <span>Bulk description</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    description_append: event.target.value,
                                                  }))
                                                }
                                                placeholder="shared governance note"
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.description_append}
                                              />
                                            </label>
                                            <label>
                                              <span>Bulk template link</span>
                                              <select
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    template_id: event.target.value,
                                                  }))
                                                }
                                                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.template_id}
                                              >
                                                <option value="">Keep current link</option>
                                                {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                                                  <option key={entry.template_id} value={entry.template_id}>
                                                    {entry.name}
                                                  </option>
                                                ))}
                                              </select>
                                            </label>
                                            <label>
                                              <span>Clear link</span>
                                              <input
                                                checked={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.clear_template_link}
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    clear_template_link: event.target.checked,
                                                  }))
                                                }
                                                type="checkbox"
                                              />
                                            </label>
                                            <label>
                                              <span>Action</span>
                                              <button
                                                className="ghost-button"
                                                disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length}
                                                onClick={() => {
                                                  void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction("delete");
                                                }}
                                                type="button"
                                              >
                                                {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction === "delete"
                                                  ? "Deleting…"
                                                  : "Delete selected"}
                                              </button>
                                            </label>
                                            <label>
                                              <span>Action</span>
                                              <button
                                                className="ghost-button"
                                                disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length}
                                                onClick={() => {
                                                  void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction("update");
                                                }}
                                                type="button"
                                              >
                                                {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction === "update"
                                                  ? "Updating…"
                                                  : "Update selected"}
                                              </button>
                                            </label>
                                          </div>
                                          <div className="filter-bar">
                                            <label>
                                              <span>Bulk query patch</span>
                                              <textarea
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    query_patch: event.target.value,
                                                  }))
                                                }
                                                placeholder='{"scheduler_alert_status":"resolved"}'
                                                rows={3}
                                                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.query_patch}
                                              />
                                            </label>
                                            <label>
                                              <span>Bulk layout patch</span>
                                              <textarea
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                                                    ...current,
                                                    layout_patch: event.target.value,
                                                  }))
                                                }
                                                placeholder='{"show_recent_exports":true}'
                                                rows={3}
                                                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.layout_patch}
                                              />
                                            </label>
                                          </div>
                                          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length ? (
                                            <table className="data-table">
                                              <thead>
                                                <tr>
                                                  <th aria-label="Select step">Sel</th>
                                                  <th>Step</th>
                                                  <th>Patch</th>
                                                  <th>Action</th>
                                                </tr>
                                              </thead>
                                              <tbody>
                                                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.map((step, index) => (
                                                  <tr key={step.step_id ?? `${step.item_type}-${index}`}>
                                                    <td>
                                                      <input
                                                        checked={step.step_id ? selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet.has(step.step_id) : false}
                                                        disabled={!step.step_id}
                                                        onChange={() => {
                                                          if (step.step_id) {
                                                            toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelection(step.step_id);
                                                          }
                                                        }}
                                                        type="checkbox"
                                                      />
                                                    </td>
                                                    <td>
                                                      <strong>{step.step_id ?? `step ${index + 1}`}</strong>
                                                      <p className="run-lineage-symbol-copy">
                                                        {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(step)}
                                                      </p>
                                                      {step.source_template_name || step.source_template_id ? (
                                                        <p className="run-lineage-symbol-copy">
                                                          Source template: {step.source_template_name ?? step.source_template_id}
                                                        </p>
                                                      ) : null}
                                                      <p className="run-lineage-symbol-copy">
                                                        {index + 1} of {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length}
                                                      </p>
                                                    </td>
                                                    <td>
                                                      <strong>{step.item_ids.length} target(s)</strong>
                                                      <p className="run-lineage-symbol-copy">
                                                        {step.item_ids.join(", ")}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">
                                                        {Object.keys(step.query_patch ?? {}).length
                                                          ? `query ${JSON.stringify(step.query_patch)}`
                                                          : "no query patch"}
                                                        {step.item_type === "registry"
                                                          ? ` · ${
                                                              Object.keys(step.layout_patch ?? {}).length
                                                                ? `layout ${JSON.stringify(step.layout_patch)}`
                                                                : "no layout patch"
                                                            }`
                                                          : ""}
                                                      </p>
                                                    </td>
                                                    <td>
                                                      <div className="market-data-provenance-history-actions">
                                                        <button
                                                          className="ghost-button"
                                                          disabled={!step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
                                                          onClick={() => {
                                                            editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep(step);
                                                          }}
                                                          type="button"
                                                        >
                                                          Edit
                                                        </button>
                                                        <button
                                                          className="ghost-button"
                                                          disabled={!step.step_id}
                                                          onClick={() => {
                                                            setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId(
                                                              step.step_id ?? null,
                                                            );
                                                          }}
                                                          type="button"
                                                        >
                                                          Versions
                                                        </button>
                                                      </div>
                                                    </td>
                                                  </tr>
                                                ))}
                                              </tbody>
                                            </table>
                                          ) : (
                                            <p className="empty-state">No hierarchy steps are currently captured on this policy catalog.</p>
                                          )}
                                          <div className="market-data-provenance-shared-history">
                                            <div className="market-data-provenance-history-head">
                                              <strong>Hierarchy step editor</strong>
                                              <p>Edit one captured step directly. Empty JSON clears the current patch.</p>
                                            </div>
                                            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
                                              <div className="filter-bar">
                                                <label>
                                                  <span>Targets</span>
                                                  <input
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                        ...current,
                                                        item_ids_text: event.target.value,
                                                      }))
                                                    }
                                                    placeholder="id_1, id_2"
                                                    type="text"
                                                    value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.item_ids_text}
                                                  />
                                                </label>
                                                <label>
                                                  <span>Name prefix</span>
                                                  <input
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                        ...current,
                                                        name_prefix: event.target.value,
                                                      }))
                                                    }
                                                    placeholder="Reviewed / "
                                                    type="text"
                                                    value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.name_prefix}
                                                  />
                                                </label>
                                                <label>
                                                  <span>Name suffix</span>
                                                  <input
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                        ...current,
                                                        name_suffix: event.target.value,
                                                      }))
                                                    }
                                                    placeholder=" / approved"
                                                    type="text"
                                                    value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.name_suffix}
                                                  />
                                                </label>
                                                <label>
                                                  <span>Description</span>
                                                  <input
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                        ...current,
                                                        description_append: event.target.value,
                                                      }))
                                                    }
                                                    placeholder="shared governance note"
                                                    type="text"
                                                    value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.description_append}
                                                  />
                                                </label>
                                                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep.item_type === "registry" ? (
                                                  <>
                                                    <label>
                                                      <span>Template link</span>
                                                      <select
                                                        onChange={(event) =>
                                                          setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                            ...current,
                                                            template_id: event.target.value,
                                                          }))
                                                        }
                                                        value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.template_id}
                                                      >
                                                        <option value="">No explicit template link</option>
                                                        {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                                                          <option key={entry.template_id} value={entry.template_id}>
                                                            {entry.name}
                                                          </option>
                                                        ))}
                                                      </select>
                                                    </label>
                                                    <label>
                                                      <span>Clear link</span>
                                                      <input
                                                        checked={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.clear_template_link}
                                                        onChange={(event) =>
                                                          setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                            ...current,
                                                            clear_template_link: event.target.checked,
                                                          }))
                                                        }
                                                        type="checkbox"
                                                      />
                                                    </label>
                                                  </>
                                                ) : null}
                                                <label>
                                                  <span>Action</span>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={() => {
                                                      void saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep();
                                                    }}
                                                    type="button"
                                                  >
                                                    Save step
                                                  </button>
                                                </label>
                                                <label>
                                                  <span>Action</span>
                                                  <button
                                                    className="ghost-button"
                                                    onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft}
                                                    type="button"
                                                  >
                                                    Clear draft
                                                  </button>
                                                </label>
                                              </div>
                                            ) : (
                                              <p className="empty-state">Select a hierarchy step row and choose Edit to stage it in the editor.</p>
                                            )}
                                            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
                                              <div className="filter-bar">
                                                <label>
                                                  <span>Query patch</span>
                                                  <textarea
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                        ...current,
                                                        query_patch: event.target.value,
                                                      }))
                                                    }
                                                    placeholder='{"scheduler_alert_status":"resolved"}'
                                                    rows={4}
                                                    value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.query_patch}
                                                  />
                                                </label>
                                                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep.item_type === "registry" ? (
                                                  <label>
                                                    <span>Layout patch</span>
                                                    <textarea
                                                      onChange={(event) =>
                                                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                                                          ...current,
                                                          layout_patch: event.target.value,
                                                        }))
                                                      }
                                                      placeholder='{"show_recent_exports":true}'
                                                      rows={4}
                                                      value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.layout_patch}
                                                    />
                                                  </label>
                                                ) : null}
                                              </div>
                                            ) : null}
                                          </div>
                                          <div className="market-data-provenance-shared-history">
                                            <div className="market-data-provenance-history-head">
                                              <strong>Hierarchy step versions</strong>
                                              <p>Use the loaded catalog revision history to stage a prior step snapshot or restore that step only.</p>
                                            </div>
                                            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.length ? (
                                              <table className="data-table">
                                                <thead>
                                                  <tr>
                                                    <th>Revision</th>
                                                    <th>Step</th>
                                                    <th>Action</th>
                                                  </tr>
                                                </thead>
                                                <tbody>
                                                  {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.map((entry) => (
                                                    <tr key={`${entry.revision.revision_id}:${entry.step.step_id ?? "step"}`}>
                                                      <td>
                                                        <strong>{entry.revision.revision_id}</strong>
                                                        <p className="run-lineage-symbol-copy">
                                                          {entry.revision.reason}
                                                        </p>
                                                        <p className="run-lineage-symbol-copy">
                                                          {formatTimestamp(entry.revision.recorded_at)}
                                                        </p>
                                                      </td>
                                                      <td>
                                                        <strong>{entry.step.step_id ?? "unknown step"}</strong>
                                                        <p className="run-lineage-symbol-copy">
                                                          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                                                        </p>
                                                        {entry.step.source_template_name || entry.step.source_template_id ? (
                                                          <p className="run-lineage-symbol-copy">
                                                            Source template: {entry.step.source_template_name ?? entry.step.source_template_id}
                                                          </p>
                                                        ) : null}
                                                        <p className="run-lineage-symbol-copy">
                                                          {entry.position} of {entry.total}
                                                        </p>
                                                      </td>
                                                      <td>
                                                        <div className="market-data-provenance-history-actions">
                                                          <button
                                                            className="ghost-button"
                                                            onClick={() => {
                                                              stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft(entry.step);
                                                            }}
                                                            type="button"
                                                          >
                                                            Stage draft
                                                          </button>
                                                          <button
                                                            className="ghost-button"
                                                            disabled={!entry.step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
                                                            onClick={() => {
                                                              void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersion(entry);
                                                            }}
                                                            type="button"
                                                          >
                                                            Restore step
                                                          </button>
                                                        </div>
                                                      </td>
                                                    </tr>
                                                  ))}
                                                </tbody>
                                              </table>
                                            ) : (
                                              <p className="empty-state">Select a hierarchy step and open Versions to inspect step snapshots across catalog revisions.</p>
                                            )}
                                          </div>
                                        </>
                                      ) : (
                                        <p className="empty-state">Select a policy catalog row and open Versions to inspect hierarchy steps.</p>
                                      )}
                                    </div>
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Named hierarchy step templates</strong>
                                        <p>Promote a captured hierarchy step into a reusable template, version it, and bulk-govern it across policy catalogs.</p>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Template name</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                ...current,
                                                name: event.target.value,
                                              }))
                                            }
                                            placeholder="Cross-catalog registry sync"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.name}
                                          />
                                        </label>
                                        <label>
                                          <span>Description</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                ...current,
                                                description: event.target.value,
                                              }))
                                            }
                                            placeholder="Reusable sync step for scheduler governance catalogs"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.description}
                                          />
                                        </label>
                                        <label>
                                          <span>Current source</span>
                                          <strong className="comparison-history-export-copy">
                                            {editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId
                                              ? selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate
                                                ? `${selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate.name} · ${formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(
                                                    selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate.step,
                                                  )}`
                                                : "Template no longer selected"
                                              : selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep
                                                ? formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(
                                                    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
                                                  )
                                                : "No step selected"}
                                          </strong>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <button
                                            className="ghost-button"
                                            disabled={
                                              !editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId
                                              && !selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep
                                            }
                                            onClick={() => {
                                              if (editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId) {
                                                void saveProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateFromStep(
                                                  selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate?.step ?? {
                                                    item_type: "template",
                                                    action: "update",
                                                    item_ids: [],
                                                    item_names: [],
                                                    query_patch: {},
                                                    layout_patch: {},
                                                    clear_template_link: false,
                                                  },
                                                );
                                              } else if (selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep) {
                                                void saveProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateFromStep(
                                                  selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
                                                );
                                              }
                                            }}
                                            type="button"
                                          >
                                            {editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId
                                              ? "Save template"
                                              : "Save selected step"}
                                          </button>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <button
                                            className="ghost-button"
                                            onClick={resetProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft}
                                            type="button"
                                          >
                                            Clear draft
                                          </button>
                                        </label>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Policy catalog</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                ...current,
                                                governance_policy_catalog_id: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.governance_policy_catalog_id}
                                          >
                                            <option value="">No saved policy catalog</option>
                                            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs
                                              .filter((entry) => entry.status === "active")
                                              .map((entry) => (
                                                <option key={entry.catalog_id} value={entry.catalog_id}>
                                                  {entry.name}
                                                </option>
                                              ))}
                                          </select>
                                        </label>
                                        <label>
                                          <span>Policy template</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                ...current,
                                                governance_policy_template_id: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.governance_policy_template_id}
                                          >
                                            <option value="">No saved policy template</option>
                                            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                                              .filter((entry) => entry.status === "active")
                                              .map((entry) => (
                                                <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                                  {entry.name}
                                                </option>
                                              ))}
                                          </select>
                                        </label>
                                        <label>
                                          <span>Approval lane</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                ...current,
                                                governance_approval_lane: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.governance_approval_lane}
                                          >
                                            <option value="">Use policy default lane</option>
                                            <option value="ops_review">Ops review</option>
                                            <option value="shift_lead">Shift lead</option>
                                            <option value="risk_review">Risk review</option>
                                            <option value="incident_command">Incident command</option>
                                          </select>
                                        </label>
                                        <label>
                                          <span>Approval priority</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                ...current,
                                                governance_approval_priority: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.governance_approval_priority}
                                          >
                                            <option value="">Use policy default priority</option>
                                            <option value="low">Low</option>
                                            <option value="normal">Normal</option>
                                            <option value="high">High</option>
                                            <option value="critical">Critical</option>
                                          </select>
                                        </label>
                                      </div>
                                      {editingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId
                                      && selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate ? (
                                        <>
                                          <div className="filter-bar">
                                            <label>
                                              <span>Targets</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                    ...current,
                                                    item_ids_text: event.target.value,
                                                  }))
                                                }
                                                placeholder="id_1, id_2"
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.item_ids_text}
                                              />
                                            </label>
                                            <label>
                                              <span>Step name prefix</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                    ...current,
                                                    name_prefix: event.target.value,
                                                  }))
                                                }
                                                placeholder="Reviewed / "
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.name_prefix}
                                              />
                                            </label>
                                            <label>
                                              <span>Step name suffix</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                    ...current,
                                                    name_suffix: event.target.value,
                                                  }))
                                                }
                                                placeholder=" / approved"
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.name_suffix}
                                              />
                                            </label>
                                            <label>
                                              <span>Step description</span>
                                              <input
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                    ...current,
                                                    description_append: event.target.value,
                                                  }))
                                                }
                                                placeholder="shared governance note"
                                                type="text"
                                                value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.description_append}
                                              />
                                            </label>
                                            {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate.item_type === "registry" ? (
                                              <>
                                                <label>
                                                  <span>Template link</span>
                                                  <select
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                        ...current,
                                                        template_id: event.target.value,
                                                      }))
                                                    }
                                                    value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.template_id}
                                                  >
                                                    <option value="">No explicit template link</option>
                                                    {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                                                      <option key={entry.template_id} value={entry.template_id}>
                                                        {entry.name}
                                                      </option>
                                                    ))}
                                                  </select>
                                                </label>
                                                <label>
                                                  <span>Clear link</span>
                                                  <input
                                                    checked={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.clear_template_link}
                                                    onChange={(event) =>
                                                      setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                        ...current,
                                                        clear_template_link: event.target.checked,
                                                      }))
                                                    }
                                                    type="checkbox"
                                                  />
                                                </label>
                                              </>
                                            ) : null}
                                          </div>
                                          <div className="filter-bar">
                                            <label>
                                              <span>Query patch</span>
                                              <textarea
                                                onChange={(event) =>
                                                  setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                    ...current,
                                                    query_patch: event.target.value,
                                                  }))
                                                }
                                                placeholder='{"scheduler_alert_status":"resolved"}'
                                                rows={4}
                                                value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.query_patch}
                                              />
                                            </label>
                                            {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate.item_type === "registry" ? (
                                              <label>
                                                <span>Layout patch</span>
                                                <textarea
                                                  onChange={(event) =>
                                                    setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft((current) => ({
                                                      ...current,
                                                      layout_patch: event.target.value,
                                                    }))
                                                  }
                                                  placeholder='{"show_recent_exports":true}'
                                                  rows={4}
                                                  value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft.layout_patch}
                                                />
                                              </label>
                                            ) : null}
                                          </div>
                                        </>
                                      ) : null}
                                      <div className="filter-bar">
                                        <label>
                                          <span>Selection</span>
                                          <button
                                            className="ghost-button"
                                            disabled={!providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length}
                                            onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelections}
                                            type="button"
                                          >
                                            {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length
                                              === providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length
                                              && providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length
                                                ? "Clear all"
                                                : "Select all"}
                                          </button>
                                        </label>
                                        <label>
                                          <span>Bulk name prefix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                name_prefix: event.target.value,
                                              }))
                                            }
                                            placeholder="Reviewed / "
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.name_prefix}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk name suffix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                name_suffix: event.target.value,
                                              }))
                                            }
                                            placeholder=" / staged"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.name_suffix}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk description</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                description_append: event.target.value,
                                              }))
                                            }
                                            placeholder="team rollout"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.description_append}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk targets</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                item_ids_text: event.target.value,
                                              }))
                                            }
                                            placeholder="optional override ids"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.item_ids_text}
                                          />
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <button
                                            className="ghost-button"
                                            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
                                            onClick={() => {
                                              void runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction("delete");
                                            }}
                                            type="button"
                                          >
                                            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "delete"
                                              ? "Deleting…"
                                              : "Delete selected"}
                                          </button>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <button
                                            className="ghost-button"
                                            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
                                            onClick={() => {
                                              void runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction("restore");
                                            }}
                                            type="button"
                                          >
                                            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "restore"
                                              ? "Restoring…"
                                              : "Restore selected"}
                                          </button>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <button
                                            className="ghost-button"
                                            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
                                            onClick={() => {
                                              void stageSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates();
                                            }}
                                            type="button"
                                          >
                                            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "stage"
                                              ? "Staging…"
                                              : "Stage selected"}
                                          </button>
                                        </label>
                                        <label>
                                          <span>Action</span>
                                          <button
                                            className="ghost-button"
                                            disabled={!selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds.length}
                                            onClick={() => {
                                              void runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction("update");
                                            }}
                                            type="button"
                                          >
                                            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkAction === "update"
                                              ? "Updating…"
                                              : "Update selected"}
                                          </button>
                                        </label>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Bulk step prefix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                step_name_prefix: event.target.value,
                                              }))
                                            }
                                            placeholder="Reviewed / "
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.step_name_prefix}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk step suffix</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                step_name_suffix: event.target.value,
                                              }))
                                            }
                                            placeholder=" / approved"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.step_name_suffix}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk step description</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                step_description_append: event.target.value,
                                              }))
                                            }
                                            placeholder="shared patch note"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.step_description_append}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk template link</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                template_id: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.template_id}
                                          >
                                            <option value="">Keep current link</option>
                                            {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                                              <option key={entry.template_id} value={entry.template_id}>
                                                {entry.name}
                                              </option>
                                            ))}
                                          </select>
                                        </label>
                                        <label>
                                          <span>Clear link</span>
                                          <input
                                            checked={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.clear_template_link}
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                clear_template_link: event.target.checked,
                                              }))
                                            }
                                            type="checkbox"
                                          />
                                        </label>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Bulk query patch</span>
                                          <textarea
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                query_patch: event.target.value,
                                              }))
                                            }
                                            placeholder='{"scheduler_alert_status":"resolved"}'
                                            rows={3}
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.query_patch}
                                          />
                                        </label>
                                        <label>
                                          <span>Bulk layout patch</span>
                                          <textarea
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft((current) => ({
                                                ...current,
                                                layout_patch: event.target.value,
                                              }))
                                            }
                                            placeholder='{"show_recent_exports":true}'
                                            rows={3}
                                            value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkDraft.layout_patch}
                                          />
                                        </label>
                                      </div>
                                      <p className="run-lineage-symbol-copy">
                                        Target catalogs: {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds.length
                                          || (selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog ? 1 : 0)}
                                        {" "}selected for cross-catalog apply.
                                      </p>
                                      {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesLoading ? (
                                        <p className="empty-state">Loading hierarchy step templates…</p>
                                      ) : null}
                                      {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesError ? (
                                        <p className="market-data-workflow-feedback">
                                          Hierarchy step template load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesError}
                                        </p>
                                      ) : null}
                                      {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th aria-label="Select template">Sel</th>
                                              <th>Template</th>
                                              <th>Origin</th>
                                              <th>Action</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
                                              <tr key={entry.hierarchy_step_template_id}>
                                                <td>
                                                  <input
                                                    checked={selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIdSet.has(entry.hierarchy_step_template_id)}
                                                    onChange={() => {
                                                      toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelection(
                                                        entry.hierarchy_step_template_id,
                                                      );
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
                                                    {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatWorkflowToken(entry.status)} · revision {entry.revision_count}
                                                    {entry.current_revision_id ? ` · ${shortenIdentifier(entry.current_revision_id, 10)}` : ""}
                                                  </p>
                                                  {(entry.governance_policy_template_name || entry.governance_policy_catalog_name || entry.governance_approval_lane || entry.governance_approval_priority) ? (
                                                    <p className="run-lineage-symbol-copy">
                                                      Queue policy: {entry.governance_policy_template_name ?? "no template"}
                                                      {entry.governance_policy_catalog_name ? ` · ${entry.governance_policy_catalog_name}` : ""}
                                                      {entry.governance_approval_lane ? ` · ${formatWorkflowToken(entry.governance_approval_lane)}` : ""}
                                                      {entry.governance_approval_priority ? ` · ${formatWorkflowToken(entry.governance_approval_priority)}` : ""}
                                                    </p>
                                                  ) : (
                                                    <p className="run-lineage-symbol-copy">Queue policy: ad hoc at stage time</p>
                                                  )}
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"} · updated {formatTimestamp(entry.updated_at)}
                                                  </p>
                                                </td>
                                                <td>
                                                  <strong>{entry.origin_catalog_name ?? "Ad hoc step template"}</strong>
                                                  <p className="run-lineage-symbol-copy">
                                                    {entry.origin_step_id ? `Origin step ${entry.origin_step_id}` : "Saved from direct step payload"}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId === entry.hierarchy_step_template_id
                                                      ? "Selected for cross-catalog governance"
                                                      : "Available for cross-catalog governance"}
                                                  </p>
                                                  {entry.governance_policy_guidance ? (
                                                    <p className="run-lineage-symbol-copy">
                                                      Guidance: {entry.governance_policy_guidance}
                                                    </p>
                                                  ) : null}
                                                </td>
                                                <td>
                                                  <div className="market-data-provenance-history-actions">
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        setSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId(
                                                          entry.hierarchy_step_template_id,
                                                        );
                                                        setProviderProvenanceWorkspaceFeedback(
                                                          `Selected hierarchy step template ${entry.name} for cross-catalog governance.`,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Use template
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        editProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(
                                                          entry,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Edit
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      onClick={() => {
                                                        void toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory(
                                                          entry.hierarchy_step_template_id,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Versions
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateQueuePlan(
                                                          entry,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Stage queue
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateToCatalogs(
                                                          entry,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Apply to selected catalogs
                                                    </button>
                                                    <button
                                                      className="ghost-button"
                                                      disabled={entry.status !== "active"}
                                                      onClick={() => {
                                                        void removeProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(
                                                          entry,
                                                        );
                                                      }}
                                                      type="button"
                                                    >
                                                      Delete
                                                    </button>
                                                  </div>
                                                </td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      ) : (
                                        <p className="empty-state">No hierarchy step templates saved yet.</p>
                                      )}
                                      {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate ? (
                                        <div className="market-data-provenance-shared-history">
                                          <div className="market-data-provenance-history-head">
                                            <strong>Template versions</strong>
                                            <p>Stage a prior snapshot into the editor or restore a specific revision.</p>
                                          </div>
                                          {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryLoading ? (
                                            <p className="empty-state">Loading hierarchy step template revisions…</p>
                                          ) : null}
                                          {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryError ? (
                                            <p className="market-data-workflow-feedback">
                                              Hierarchy step template revision load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryError}
                                            </p>
                                          ) : null}
                                          {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory ? (
                                            <table className="data-table">
                                              <thead>
                                                <tr>
                                                  <th>Revision</th>
                                                  <th>Template</th>
                                                  <th>Action</th>
                                                </tr>
                                              </thead>
                                              <tbody>
                                                {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory.history.map((entry) => (
                                                  <tr key={entry.revision_id}>
                                                    <td>
                                                      <strong>{entry.revision_id}</strong>
                                                      <p className="run-lineage-symbol-copy">
                                                        {entry.reason}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">
                                                        {formatTimestamp(entry.recorded_at)}
                                                      </p>
                                                    </td>
                                                    <td>
                                                      <strong>{entry.name}</strong>
                                                      <p className="run-lineage-symbol-copy">
                                                        {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                                                      </p>
                                                      <p className="run-lineage-symbol-copy">
                                                        {formatWorkflowToken(entry.status)}
                                                        {entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
                                                      </p>
                                                    </td>
                                                    <td>
                                                      <div className="market-data-provenance-history-actions">
                                                        <button
                                                          className="ghost-button"
                                                          onClick={() => {
                                                            setEditingProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId(
                                                              entry.hierarchy_step_template_id,
                                                            );
                                                            setSelectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId(
                                                              entry.hierarchy_step_template_id,
                                                            );
                                                            setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateDraft({
                                                              name: entry.name,
                                                              description: entry.description,
                                                              item_ids_text: entry.step.item_ids.join(", "),
                                                              name_prefix: entry.step.name_prefix ?? "",
                                                              name_suffix: entry.step.name_suffix ?? "",
                                                              description_append: entry.step.description_append ?? "",
                                                              query_patch: Object.keys(entry.step.query_patch ?? {}).length
                                                                ? JSON.stringify(entry.step.query_patch, null, 2)
                                                                : "",
                                                              layout_patch: Object.keys(entry.step.layout_patch ?? {}).length
                                                                ? JSON.stringify(entry.step.layout_patch, null, 2)
                                                                : "",
                                                              template_id: entry.step.template_id ?? "",
                                                              clear_template_link: entry.step.clear_template_link,
                                                              governance_policy_template_id: entry.governance_policy_template_id ?? "",
                                                              governance_policy_catalog_id: entry.governance_policy_catalog_id ?? "",
                                                              governance_approval_lane: entry.governance_approval_lane ?? "",
                                                              governance_approval_priority: entry.governance_approval_priority ?? "",
                                                            });
                                                            setProviderProvenanceWorkspaceFeedback(
                                                              `Hierarchy step template revision ${entry.revision_id} staged in the editor.`,
                                                            );
                                                          }}
                                                          type="button"
                                                        >
                                                          Stage draft
                                                        </button>
                                                        <button
                                                          className="ghost-button"
                                                          onClick={() => {
                                                            void restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistoryRevision(
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
                                            <p className="empty-state">Select a hierarchy step template row and open Versions to inspect revisions.</p>
                                          )}
                                        </div>
                                      ) : null}
                                      <div className="market-data-provenance-shared-history">
                                        <div className="market-data-provenance-history-head">
                                          <strong>Hierarchy step template team audit</strong>
                                          <p>Filter lifecycle and bulk-governance events by template, action, or actor to review who changed reusable cross-catalog steps.</p>
                                        </div>
                                        <div className="filter-bar">
                                          <label>
                                            <span>Template</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                                                  ...current,
                                                  hierarchy_step_template_id: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.hierarchy_step_template_id}
                                            >
                                              <option value="">All templates</option>
                                              {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
                                                <option key={entry.hierarchy_step_template_id} value={entry.hierarchy_step_template_id}>
                                                  {entry.name}
                                                </option>
                                              ))}
                                            </select>
                                          </label>
                                          <label>
                                            <span>Action</span>
                                            <select
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                                                  ...current,
                                                  action: event.target.value,
                                                }))
                                              }
                                              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.action}
                                            >
                                              <option value={ALL_FILTER_VALUE}>All actions</option>
                                              <option value="created">Created</option>
                                              <option value="updated">Updated</option>
                                              <option value="staged">Staged</option>
                                              <option value="deleted">Deleted</option>
                                              <option value="restored">Restored</option>
                                            </select>
                                          </label>
                                          <label>
                                            <span>Actor</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                                                  ...current,
                                                  actor_tab_id: event.target.value,
                                                }))
                                              }
                                              placeholder="tab_ops"
                                              type="text"
                                              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.actor_tab_id}
                                            />
                                          </label>
                                          <label>
                                            <span>Search</span>
                                            <input
                                              onChange={(event) =>
                                                setProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter((current) => ({
                                                  ...current,
                                                  search: event.target.value,
                                                }))
                                              }
                                              placeholder="cross-catalog, bulk"
                                              type="search"
                                              value={providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditFilter.search}
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
                                        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsLoading ? (
                                          <p className="empty-state">Loading hierarchy step template audit trail…</p>
                                        ) : null}
                                        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError ? (
                                          <p className="market-data-workflow-feedback">
                                            Hierarchy step template audit load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError}
                                          </p>
                                        ) : null}
                                        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits.length ? (
                                          <table className="data-table">
                                            <thead>
                                              <tr>
                                                <th>Audit</th>
                                                <th>Template</th>
                                                <th>Actor</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits.map((entry) => (
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
                                                      {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                                                    </p>
                                                    {(entry.governance_policy_template_name || entry.governance_policy_catalog_name || entry.governance_approval_lane || entry.governance_approval_priority) ? (
                                                      <p className="run-lineage-symbol-copy">
                                                        Queue policy: {entry.governance_policy_template_name ?? "no template"}
                                                        {entry.governance_policy_catalog_name ? ` · ${entry.governance_policy_catalog_name}` : ""}
                                                        {entry.governance_approval_lane ? ` · ${formatWorkflowToken(entry.governance_approval_lane)}` : ""}
                                                        {entry.governance_approval_priority ? ` · ${formatWorkflowToken(entry.governance_approval_priority)}` : ""}
                                                      </p>
                                                    ) : null}
                                                    <p className="run-lineage-symbol-copy">
                                                      {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.item_type)}
                                                      {entry.origin_catalog_name ? ` · ${entry.origin_catalog_name}` : " · ad hoc source"}
                                                    </p>
                                                    <p className="run-lineage-symbol-copy">
                                                      revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
                                                    </p>
                                                  </td>
                                                  <td>
                                                    <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "system"}</strong>
                                                    <p className="run-lineage-symbol-copy">
                                                      {entry.reason}
                                                    </p>
                                                    <p className="run-lineage-symbol-copy">
                                                      {entry.origin_step_id ? `Origin step ${entry.origin_step_id}` : "No origin step"}
                                                    </p>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        ) : (
                                          <p className="empty-state">No hierarchy step template audit records match the current filter.</p>
                                        )}
                                      </div>
                                    </div>
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Policy catalog team audit</strong>
                                        <p>Filter shared audit events by catalog, action, or actor to review catalog lifecycle and linked-template changes.</p>
                                      </div>
                                      <div className="filter-bar">
                                        <label>
                                          <span>Catalog</span>
                                          <select
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                                                ...current,
                                                catalog_id: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.catalog_id}
                                          >
                                            <option value="">All catalogs</option>
                                            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((entry) => (
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
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                                                ...current,
                                                action: event.target.value,
                                              }))
                                            }
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.action}
                                          >
                                            <option value={ALL_FILTER_VALUE}>All actions</option>
                                            <option value="created">Created</option>
                                            <option value="updated">Updated</option>
                                            <option value="hierarchy_captured">Hierarchy captured</option>
                                            <option value="hierarchy_step_updated">Hierarchy step updated</option>
                                            <option value="hierarchy_step_restored">Hierarchy step restored</option>
                                            <option value="hierarchy_steps_bulk_updated">Hierarchy steps bulk updated</option>
                                            <option value="hierarchy_steps_bulk_deleted">Hierarchy steps bulk deleted</option>
                                            <option value="staged">Staged</option>
                                            <option value="deleted">Deleted</option>
                                            <option value="restored">Restored</option>
                                          </select>
                                        </label>
                                        <label>
                                          <span>Actor</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                                                ...current,
                                                actor_tab_id: event.target.value,
                                              }))
                                            }
                                            placeholder="tab_ops"
                                            type="text"
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.actor_tab_id}
                                          />
                                        </label>
                                        <label>
                                          <span>Search</span>
                                          <input
                                            onChange={(event) =>
                                              setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter((current) => ({
                                                ...current,
                                                search: event.target.value,
                                              }))
                                            }
                                            placeholder="batch, restore, default"
                                            type="search"
                                            value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditFilter.search}
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
                                      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsLoading ? (
                                        <p className="empty-state">Loading policy catalog audit trail…</p>
                                      ) : null}
                                      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsError ? (
                                        <p className="market-data-workflow-feedback">
                                          Policy catalog audit load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditsError}
                                        </p>
                                      ) : null}
                                      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits.length ? (
                                        <table className="data-table">
                                          <thead>
                                            <tr>
                                              <th>Audit</th>
                                              <th>Catalog</th>
                                              <th>Actor</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits.map((entry) => (
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
                                                    {formatWorkflowToken(entry.status)} · {entry.policy_template_names.join(", ") || "No linked templates."}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
                                                  </p>
                                                  <p className="run-lineage-symbol-copy">
                                                    {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(entry.hierarchy_steps)}
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
                                        <p className="empty-state">No policy catalog audit records match the current filter.</p>
                                      )}
                                    </div>
                                  </div>
                                </div>
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
                                          {selectedProviderProvenanceSchedulerNarrativeTemplateEntries.filter((entry) => entry.status === "active").length} active · {" "}
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
                                          {selectedProviderProvenanceSchedulerNarrativeRegistryEntries.filter((entry) => entry.status === "active").length} active · {" "}
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
                                <div className="provider-provenance-workspace-card">
                                  <div className="market-data-provenance-history-head">
                                    <strong>Approval queue</strong>
                                    <p>Review staged scheduler governance plans by lane and priority, approve them, then apply or roll back against the captured revision snapshot.</p>
                                  </div>
                                  <div className="provider-provenance-governance-summary">
                                    <strong>
                                      Pending {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.pending_approval_count} · Ready {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.ready_to_apply_count} · Completed {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.completed_count}
                                    </strong>
                                    <span>
                                      Filtered queue rows: {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} of {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.total}
                                    </span>
                                  </div>
                                  <div className="provider-provenance-governance-editor">
                                    <div className="market-data-provenance-history-head">
                                      <strong>Batch queue actions</strong>
                                      <p>Approve or apply multiple governance plans at once after filtering the queue to the exact lane, priority, or policy template slice you want.</p>
                                    </div>
                                    <div className="provider-provenance-governance-summary">
                                      <strong>
                                        Selected {selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} of {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} filtered plan(s)
                                      </strong>
                                      <span>
                                        {selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.map((plan) => shortenIdentifier(plan.plan_id, 8)).join(", ") || "No plans selected"}
                                      </span>
                                    </div>
                                    <div className="market-data-provenance-history-actions">
                                      <button
                                        className="ghost-button"
                                        onClick={toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections}
                                        type="button"
                                      >
                                        {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length > 0
                                          && selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length === filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length
                                          ? "Clear filtered"
                                          : "Select filtered"}
                                      </button>
                                      <button
                                        className="ghost-button"
                                        disabled={!selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length || providerProvenanceSchedulerNarrativeGovernanceBatchAction !== null}
                                        onClick={() => {
                                          void runProviderProvenanceSchedulerNarrativeGovernancePlanBatch("approve");
                                        }}
                                        type="button"
                                      >
                                        {providerProvenanceSchedulerNarrativeGovernanceBatchAction === "approve"
                                          ? "Approving…"
                                          : "Approve selected"}
                                      </button>
                                      <button
                                        className="ghost-button"
                                        disabled={!selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length || providerProvenanceSchedulerNarrativeGovernanceBatchAction !== null}
                                        onClick={() => {
                                          void runProviderProvenanceSchedulerNarrativeGovernancePlanBatch("apply");
                                        }}
                                        type="button"
                                      >
                                        {providerProvenanceSchedulerNarrativeGovernanceBatchAction === "apply"
                                          ? "Applying…"
                                          : "Apply selected"}
                                      </button>
                                    </div>
                                  </div>
                                  <div className="filter-bar">
                                    <label>
                                      <span>Queue state</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            queue_state:
                                              event.target.value === "pending_approval"
                                              || event.target.value === "ready_to_apply"
                                              || event.target.value === "completed"
                                                ? event.target.value
                                                : ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.queue_state}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All queue states</option>
                                        <option value="pending_approval">Pending approval</option>
                                        <option value="ready_to_apply">Ready to apply</option>
                                        <option value="completed">Completed</option>
                                      </select>
                                    </label>
                                    <label>
                                      <span>Item type</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            item_type:
                                              event.target.value === "template"
                                              || event.target.value === "registry"
                                              || event.target.value === "stitched_report_view"
                                              || event.target.value === "stitched_report_governance_registry"
                                                ? event.target.value
                                                : ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.item_type}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All item types</option>
                                        <option value="template">Templates</option>
                                        <option value="registry">Registry</option>
                                        <option value="stitched_report_view">Stitched report views</option>
                                        <option value="stitched_report_governance_registry">Stitched governance registries</option>
                                      </select>
                                    </label>
                                    <label>
                                      <span>Lane</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            approval_lane: event.target.value || ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.approval_lane}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All lanes</option>
                                        {Array.from(new Set(providerProvenanceSchedulerNarrativeGovernancePlans.map((entry) => entry.approval_lane))).sort().map((lane) => (
                                          <option key={lane} value={lane}>
                                            {formatWorkflowToken(lane)}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label>
                                      <span>Priority</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            approval_priority: event.target.value || ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.approval_priority}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All priorities</option>
                                        <option value="low">Low</option>
                                        <option value="normal">Normal</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                      </select>
                                    </label>
                                    <label>
                                      <span>Policy template</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            policy_template_id:
                                              event.target.value === ""
                                                ? ""
                                                : event.target.value || ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.policy_template_id}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All policy templates</option>
                                        <option value="">No policy template</option>
                                        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
                                          <option key={entry.policy_template_id} value={entry.policy_template_id}>
                                            {entry.name}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label>
                                      <span>Policy catalog</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            policy_catalog_id:
                                              event.target.value === ""
                                                ? ""
                                                : event.target.value || ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.policy_catalog_id}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
                                        <option value="">No policy catalog</option>
                                        {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((entry) => (
                                          <option key={entry.catalog_id} value={entry.catalog_id}>
                                            {entry.name}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label>
                                      <span>Source template</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            source_hierarchy_step_template_id:
                                              event.target.value === ""
                                                ? ""
                                                : event.target.value || ALL_FILTER_VALUE,
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.source_hierarchy_step_template_id}
                                      >
                                        <option value={ALL_FILTER_VALUE}>All source templates</option>
                                        <option value="">No source template</option>
                                        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
                                          <option key={entry.hierarchy_step_template_id} value={entry.hierarchy_step_template_id}>
                                            {entry.name}
                                          </option>
                                        ))}
                                      </select>
                                    </label>
                                    <label>
                                      <span>Search</span>
                                      <input
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            search: event.target.value,
                                          }))
                                        }
                                        placeholder="plan, template, hierarchy"
                                        type="text"
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.search}
                                      />
                                    </label>
                                    <label>
                                      <span>Sort</span>
                                      <select
                                        onChange={(event) =>
                                          setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                                            ...current,
                                            sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                                              event.target.value,
                                            ),
                                          }))
                                        }
                                        value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.sort}
                                      >
                                        <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
                                          Queue priority
                                        </option>
                                        <option value="updated_desc">Updated newest</option>
                                        <option value="updated_asc">Updated oldest</option>
                                        <option value="created_desc">Created newest</option>
                                        <option value="created_asc">Created oldest</option>
                                        <option value="source_template_asc">Source template A-Z</option>
                                        <option value="source_template_desc">Source template Z-A</option>
                                      </select>
                                    </label>
                                  </div>
                                  {providerProvenanceSchedulerNarrativeGovernancePlansLoading ? (
                                    <p className="empty-state">Loading governance plans…</p>
                                  ) : null}
                                  {providerProvenanceSchedulerNarrativeGovernancePlansError ? (
                                    <p className="market-data-workflow-feedback">
                                      Governance plan registry load failed: {providerProvenanceSchedulerNarrativeGovernancePlansError}
                                    </p>
                                  ) : null}
                                  {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length ? (
                                    <table className="data-table">
                                      <thead>
                                        <tr>
                                          <th>
                                            <input
                                              aria-label="Select all filtered governance plans"
                                              checked={
                                                filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length > 0
                                                && selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length === filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length
                                              }
                                              onChange={toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections}
                                              type="checkbox"
                                            />
                                          </th>
                                          <th>Plan</th>
                                          <th>Preview</th>
                                          <th>Action</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.map((plan) => (
                                          <tr
                                            key={plan.plan_id}
                                            className={
                                              selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
                                                ? "active-row"
                                                : undefined
                                            }
                                          >
                                            <td className="provider-provenance-selection-cell">
                                              <input
                                                aria-label={`Select governance plan ${plan.plan_id}`}
                                                checked={selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet.has(plan.plan_id)}
                                                onChange={() => {
                                                  toggleProviderProvenanceSchedulerNarrativeGovernancePlanSelection(plan.plan_id);
                                                }}
                                                type="checkbox"
                                              />
                                            </td>
                                            <td>
                                              <strong>
                                                {formatWorkflowToken(plan.action)} {plan.item_type}
                                              </strong>
                                              <p className="run-lineage-symbol-copy">
                                                {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
                                              </p>
                                              <p className="run-lineage-symbol-copy">
                                                {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}{plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}{plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
                                              </p>
                                              {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(plan) ? (
                                                <p className="run-lineage-symbol-copy">
                                                  {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(plan)}
                                                </p>
                                              ) : null}
                                              {plan.policy_catalog_name ? (
                                                <p className="run-lineage-symbol-copy">
                                                  Source catalog {plan.policy_catalog_name}
                                                </p>
                                              ) : null}
                                              {plan.source_hierarchy_step_template_name || plan.source_hierarchy_step_template_id ? (
                                                <p className="run-lineage-symbol-copy">
                                                  Source hierarchy step template {plan.source_hierarchy_step_template_name ?? plan.source_hierarchy_step_template_id}
                                                </p>
                                              ) : null}
                                            </td>
                                            <td>
                                              <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
                                              <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
                                            </td>
                                            <td>
                                              <div className="market-data-provenance-history-actions">
                                                <button
                                                  className="ghost-button"
                                                  onClick={() => {
                                                    setSelectedProviderProvenanceSchedulerNarrativeGovernancePlanId(plan.plan_id);
                                                  }}
                                                  type="button"
                                                >
                                                  {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id ? "Selected" : "Inspect"}
                                                </button>
                                              </div>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  ) : (
                                    <p className="empty-state">No scheduler governance plans match the current approval queue filters.</p>
                                  )}
                                  {selectedProviderProvenanceSchedulerNarrativeGovernancePlan ? (
                                    <div className="market-data-provenance-shared-history">
                                      <div className="market-data-provenance-history-head">
                                        <strong>Selected plan</strong>
                                        <p>
                                          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.action)} {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.item_type} · {" "}
                                          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status)} · {" "}
                                          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.length} preview row(s)
                                        </p>
                                      </div>
                                      <div className="provider-provenance-governance-summary">
                                        <strong>{selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_summary}</strong>
                                        <span>
                                          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approval_lane)} · {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approval_priority)}
                                          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_template_name
                                            ? ` · ${selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_template_name}`
                                            : ""}{" "}
                                          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_catalog_name
                                            ? ` · ${selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_catalog_name}`
                                            : ""}{" "}
                                          · {" "}
                                          Approval {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approved_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approved_at) : "pending"} · {" "}
                                          Apply {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_at) : "not applied"} · {" "}
                                          Rollback {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rolled_back_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rolled_back_at) : "not rolled back"}
                                        </span>
                                      </div>
                                      {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(selectedProviderProvenanceSchedulerNarrativeGovernancePlan) ? (
                                        <p className="run-lineage-symbol-copy">
                                          Hierarchy: {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(selectedProviderProvenanceSchedulerNarrativeGovernancePlan)}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_guidance ? (
                                        <p className="run-lineage-symbol-copy">
                                          Guidance: {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_guidance}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_name
                                      || selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_id ? (
                                        <p className="run-lineage-symbol-copy">
                                          Source hierarchy step template: {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_name
                                            ?? selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_id}
                                        </p>
                                      ) : null}
                                      <div className="market-data-provenance-history-actions">
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "previewed"
                                            || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                          }
                                          onClick={() => {
                                            void approveProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
                                          }}
                                          type="button"
                                        >
                                          {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
                                            ? "Approving…"
                                            : "Approve plan"}
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "approved"
                                            || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                          }
                                          onClick={() => {
                                            void applyProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
                                          }}
                                          type="button"
                                        >
                                          {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
                                            ? "Applying…"
                                            : "Apply approved plan"}
                                        </button>
                                        <button
                                          className="ghost-button"
                                          disabled={
                                            selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "applied"
                                            || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                                          }
                                          onClick={() => {
                                            void rollbackProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
                                          }}
                                          type="button"
                                        >
                                          {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
                                            ? "Rolling back…"
                                            : "Rollback plan"}
                                        </button>
                                      </div>
                                      <table className="data-table">
                                        <thead>
                                          <tr>
                                            <th>Item</th>
                                            <th>Diff preview</th>
                                            <th>Rollback</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.map((item) => (
                                            <tr key={item.item_id}>
                                              <td>
                                                <strong>{item.item_name ?? item.item_id}</strong>
                                                <p className="run-lineage-symbol-copy">
                                                  {formatWorkflowToken(item.outcome)} · {formatWorkflowToken(item.status ?? "unknown")}
                                                </p>
                                                <p className="run-lineage-symbol-copy">
                                                  {item.message ?? "No preview note."}
                                                </p>
                                              </td>
                                              <td>
                                                <strong>
                                                  {item.changed_fields.length ? item.changed_fields.join(", ") : "No field changes"}
                                                </strong>
                                                {item.changed_fields.length ? (
                                                  <div className="provider-provenance-governance-summary">
                                                    {item.changed_fields.map((fieldName) => (
                                                      <span key={fieldName}>
                                                        {fieldName}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.before)} {"->"}{" "}
                                                        {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.after)}
                                                      </span>
                                                    ))}
                                                  </div>
                                                ) : null}
                                              </td>
                                              <td>
                                                <strong>
                                                  {item.rollback_revision_id
                                                    ? shortenIdentifier(item.rollback_revision_id, 10)
                                                    : "No rollback revision"}
                                                </strong>
                                                <p className="run-lineage-symbol-copy">
                                                  current {item.current_revision_id ? shortenIdentifier(item.current_revision_id, 10) : "n/a"}
                                                </p>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result ? (
                                        <p className="run-lineage-symbol-copy">
                                          Apply result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result)}
                                        </p>
                                      ) : null}
                                      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result ? (
                                        <p className="run-lineage-symbol-copy">
                                          Rollback result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result)}
                                        </p>
                                      ) : null}
                                    </div>
                                  ) : null}
                                </div>
    </>
  );
}
