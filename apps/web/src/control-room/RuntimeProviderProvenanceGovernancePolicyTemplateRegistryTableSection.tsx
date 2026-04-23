// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateRegistryTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
