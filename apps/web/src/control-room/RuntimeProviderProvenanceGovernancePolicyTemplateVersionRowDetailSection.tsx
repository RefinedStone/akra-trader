// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowDetailSection({
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
    </>
  );
}
