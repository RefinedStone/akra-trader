// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowDetailSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <>
      <td>
        <strong>{entry.name}</strong>
        <p className="run-lineage-symbol-copy">
          {entry.description || "No description."}
        </p>
        <p className="run-lineage-symbol-copy">
          {entry.guidance || "No guidance."}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s) · updated {formatTimestamp(entry.updated_at)}
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
          {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
        </p>
      </td>
    </>
  );
}
