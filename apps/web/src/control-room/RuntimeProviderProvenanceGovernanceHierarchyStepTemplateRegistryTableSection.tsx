// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
