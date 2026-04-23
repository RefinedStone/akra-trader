// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowDetailSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <>
      <td>
        <strong>{entry.revision_id}</strong>
        <p className="run-lineage-symbol-copy">
          {entry.reason}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatTimestamp(entry.recorded_at)}
        </p>
      </td>
      <td>
        <strong>{entry.name}</strong>
        <p className="run-lineage-symbol-copy">
          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
        </p>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(entry.status)}
          {entry.source_revision_id ? ` · from ${shortenIdentifier(entry.source_revision_id, 10)}` : ""}
        </p>
      </td>
    </>
  );
}
