// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkStepStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
