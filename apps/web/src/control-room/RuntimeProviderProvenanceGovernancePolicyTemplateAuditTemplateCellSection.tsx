// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateAuditTemplateCellSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <strong>{entry.name}</strong>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.item_type_scope)} / {formatWorkflowToken(entry.action_scope)}
      </p>
      <p className="run-lineage-symbol-copy">
        revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
      </p>
    </td>
  );
}
