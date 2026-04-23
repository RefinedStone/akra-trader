// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td>
      <strong>{entry.detail}</strong>
      <p className="run-lineage-symbol-copy">{entry.reason}</p>
      <p className="run-lineage-symbol-copy">
        {entry.default_policy_template_name ?? "No default policy template"}
        {entry.default_policy_catalog_name
          ? ` · ${entry.default_policy_catalog_name}`
          : ""}
      </p>
    </td>
  );
}
