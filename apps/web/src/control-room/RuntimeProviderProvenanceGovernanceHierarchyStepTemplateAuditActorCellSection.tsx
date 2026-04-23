// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditActorCellSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "system"}</strong>
      <p className="run-lineage-symbol-copy">
        {entry.reason}
      </p>
      <p className="run-lineage-symbol-copy">
        {entry.origin_step_id ? `Origin step ${entry.origin_step_id}` : "No origin step"}
      </p>
    </td>
  );
}
