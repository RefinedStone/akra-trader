// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplatesSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
