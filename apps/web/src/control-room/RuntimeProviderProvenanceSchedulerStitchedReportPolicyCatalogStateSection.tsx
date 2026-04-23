// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogStateSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{catalog.name}</strong>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(catalog.status)} · {catalog.policy_template_ids.length} linked template(s)
      </p>
      <p className="run-lineage-symbol-copy">
        Scope {formatWorkflowToken(catalog.item_type_scope)} ·{" "}
        {formatWorkflowToken(catalog.action_scope)}
      </p>
      <p className="run-lineage-symbol-copy">
        {catalog.description || "No stitched report catalog description recorded."}
      </p>
    </td>
  );
}
