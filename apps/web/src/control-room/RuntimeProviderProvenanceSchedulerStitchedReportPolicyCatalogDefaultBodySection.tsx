// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDefaultBodySection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{catalog.default_policy_template_name ?? "No default policy template"}</strong>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(catalog.approval_lane)} ·{" "}
        {formatWorkflowToken(catalog.approval_priority)}
      </p>
      <p className="run-lineage-symbol-copy">
        {catalog.hierarchy_steps.length} hierarchy step(s)
      </p>
      {catalog.guidance ? (
        <p className="run-lineage-symbol-copy">{catalog.guidance}</p>
      ) : null}
    </td>
  );
}
