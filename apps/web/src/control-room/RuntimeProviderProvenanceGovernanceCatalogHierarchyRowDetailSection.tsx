// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyRowDetailSection({
  index,
  step,
}: {
  index: number;
  step: any;
}) {
  return (
    <>
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
    </>
  );
}
