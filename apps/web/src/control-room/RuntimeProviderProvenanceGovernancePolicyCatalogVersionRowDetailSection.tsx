// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowDetailSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <>
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
    </>
  );
}
