// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th aria-label="Select step">Sel</th>
          <th>Step</th>
          <th>Patch</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.map((step, index) => (
          <tr key={step.step_id ?? `${step.item_type}-${index}`}>
            <td>
              <input
                checked={step.step_id ? selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet.has(step.step_id) : false}
                disabled={!step.step_id}
                onChange={() => {
                  if (step.step_id) {
                    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelection(step.step_id);
                  }
                }}
                type="checkbox"
              />
            </td>
            <td>
              <strong>{step.step_id ?? `step ${index + 1}`}</strong>
              <p className="run-lineage-symbol-copy">
                {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(step)}
              </p>
              {step.source_template_name || step.source_template_id ? (
                <p className="run-lineage-symbol-copy">
                  Source template: {step.source_template_name ?? step.source_template_id}
                </p>
              ) : null}
              <p className="run-lineage-symbol-copy">
                {index + 1} of {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length}
              </p>
            </td>
            <td>
              <strong>{step.item_ids.length} target(s)</strong>
              <p className="run-lineage-symbol-copy">{step.item_ids.join(", ")}</p>
              <p className="run-lineage-symbol-copy">
                {Object.keys(step.query_patch ?? {}).length
                  ? `query ${JSON.stringify(step.query_patch)}`
                  : "no query patch"}
                {step.item_type === "registry"
                  ? ` · ${
                      Object.keys(step.layout_patch ?? {}).length
                        ? `layout ${JSON.stringify(step.layout_patch)}`
                        : "no layout patch"
                    }`
                  : ""}
              </p>
            </td>
            <td>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={!step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
                  onClick={() => {
                    editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep(step);
                  }}
                  type="button"
                >
                  Edit
                </button>
                <button
                  className="ghost-button"
                  disabled={!step.step_id}
                  onClick={() => {
                    setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId(
                      step.step_id ?? null,
                    );
                  }}
                  type="button"
                >
                  Versions
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  ) : (
    <p className="empty-state">No hierarchy steps are currently captured on this policy catalog.</p>
  );
}
