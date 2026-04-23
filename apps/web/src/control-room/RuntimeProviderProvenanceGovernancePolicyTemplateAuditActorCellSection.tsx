// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateAuditActorCellSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "system"}</strong>
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
      </p>
      <p className="run-lineage-symbol-copy">
        {entry.reason}
      </p>
    </td>
  );
}
