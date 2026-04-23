// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateDraftSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
