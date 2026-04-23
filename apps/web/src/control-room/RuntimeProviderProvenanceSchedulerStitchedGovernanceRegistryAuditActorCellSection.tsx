// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}</strong>
      <p className="run-lineage-symbol-copy">
        {entry.actor_tab_id ?? "No tab id recorded."}
      </p>
    </td>
  );
}
