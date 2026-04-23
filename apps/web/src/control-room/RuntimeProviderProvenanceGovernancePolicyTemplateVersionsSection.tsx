// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateVersionsSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
