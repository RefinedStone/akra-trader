// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
