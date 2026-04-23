// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogVersionsSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
