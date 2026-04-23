// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Hierarchy step versions</strong>
        <p>Use the loaded catalog revision history to stage a prior step snapshot or restore that step only.</p>
      </div>
      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Revision</th>
              <th>Step</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.map((entry) => (
              <tr key={`${entry.revision.revision_id}:${entry.step.step_id ?? "step"}`}>
                <td>
                  <strong>{entry.revision.revision_id}</strong>
                  <p className="run-lineage-symbol-copy">{entry.revision.reason}</p>
                  <p className="run-lineage-symbol-copy">{formatTimestamp(entry.revision.recorded_at)}</p>
                </td>
                <td>
                  <strong>{entry.step.step_id ?? "unknown step"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                  </p>
                  {entry.step.source_template_name || entry.step.source_template_id ? (
                    <p className="run-lineage-symbol-copy">
                      Source template: {entry.step.source_template_name ?? entry.step.source_template_id}
                    </p>
                  ) : null}
                  <p className="run-lineage-symbol-copy">
                    {entry.position} of {entry.total}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft(entry.step);
                      }}
                      type="button"
                    >
                      Stage draft
                    </button>
                    <button
                      className="ghost-button"
                      disabled={!entry.step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
                      onClick={() => {
                        void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersion(entry);
                      }}
                      type="button"
                    >
                      Restore step
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">Select a hierarchy step and open Versions to inspect step snapshots across catalog revisions.</p>
      )}
    </div>
  );
}
