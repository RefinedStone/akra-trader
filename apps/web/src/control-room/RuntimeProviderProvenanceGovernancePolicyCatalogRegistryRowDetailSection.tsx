// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogRegistryRowDetailSection({
  catalog,
}: {
  catalog: any;
}) {
  return (
    <>
      <td>
        <strong>{catalog.name}</strong>
        <p className="run-lineage-symbol-copy">
          {catalog.description || "No description."}
        </p>
        <p className="run-lineage-symbol-copy">
          {catalog.policy_template_names.join(", ") || "No linked templates."}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(catalog.status)} · {catalog.revision_count} revision(s) · updated {formatTimestamp(catalog.updated_at)}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(catalog.hierarchy_steps)}
        </p>
      </td>
      <td>
        <strong>{catalog.default_policy_template_name ?? "No default template"}</strong>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
        </p>
        <p className="run-lineage-symbol-copy">
          {catalog.created_by_tab_label ?? catalog.created_by_tab_id ?? "unknown tab"}
        </p>
      </td>
    </>
  );
}
