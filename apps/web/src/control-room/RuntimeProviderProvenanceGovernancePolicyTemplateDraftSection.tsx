// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateDraftSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
