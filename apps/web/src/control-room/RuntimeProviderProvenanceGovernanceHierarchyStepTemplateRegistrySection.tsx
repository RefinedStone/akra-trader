// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistrySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
