// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTemplateCellSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <strong>{entry.name}</strong>
      <p className="run-lineage-symbol-copy">
        {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
      </p>
      {(entry.governance_policy_template_name || entry.governance_policy_catalog_name || entry.governance_approval_lane || entry.governance_approval_priority) ? (
        <p className="run-lineage-symbol-copy">
          Queue policy: {entry.governance_policy_template_name ?? "no template"}
          {entry.governance_policy_catalog_name ? ` · ${entry.governance_policy_catalog_name}` : ""}
          {entry.governance_approval_lane ? ` · ${formatWorkflowToken(entry.governance_approval_lane)}` : ""}
          {entry.governance_approval_priority ? ` · ${formatWorkflowToken(entry.governance_approval_priority)}` : ""}
        </p>
      ) : null}
      <p className="run-lineage-symbol-copy">
        {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.item_type)}
        {entry.origin_catalog_name ? ` · ${entry.origin_catalog_name}` : " · ad hoc source"}
      </p>
      <p className="run-lineage-symbol-copy">
        revision {entry.revision_id ?? "n/a"}{entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
      </p>
    </td>
  );
}
