// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowDetailSection({
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
          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(entry.status)} · revision {entry.revision_count}
          {entry.current_revision_id ? ` · ${shortenIdentifier(entry.current_revision_id, 10)}` : ""}
        </p>
        {(entry.governance_policy_template_name || entry.governance_policy_catalog_name || entry.governance_approval_lane || entry.governance_approval_priority) ? (
          <p className="run-lineage-symbol-copy">
            Queue policy: {entry.governance_policy_template_name ?? "no template"}
            {entry.governance_policy_catalog_name ? ` · ${entry.governance_policy_catalog_name}` : ""}
            {entry.governance_approval_lane ? ` · ${formatWorkflowToken(entry.governance_approval_lane)}` : ""}
            {entry.governance_approval_priority ? ` · ${formatWorkflowToken(entry.governance_approval_priority)}` : ""}
          </p>
        ) : (
          <p className="run-lineage-symbol-copy">Queue policy: ad hoc at stage time</p>
        )}
        <p className="run-lineage-symbol-copy">
          {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"} · updated {formatTimestamp(entry.updated_at)}
        </p>
      </td>
      <td>
        <strong>{entry.origin_catalog_name ?? "Ad hoc step template"}</strong>
        <p className="run-lineage-symbol-copy">
          {entry.origin_step_id ? `Origin step ${entry.origin_step_id}` : "Saved from direct step payload"}
        </p>
        <p className="run-lineage-symbol-copy">
          {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId === entry.hierarchy_step_template_id
            ? "Selected for cross-catalog governance"
            : "Available for cross-catalog governance"}
        </p>
        {entry.governance_policy_guidance ? (
          <p className="run-lineage-symbol-copy">
            Guidance: {entry.governance_policy_guidance}
          </p>
        ) : null}
      </td>
    </>
  );
}
