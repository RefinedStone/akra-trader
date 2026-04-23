// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSummaryCellSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <strong>{formatWorkflowToken(entry.action)}</strong>
      <p className="run-lineage-symbol-copy">
        {entry.detail}
      </p>
      <p className="run-lineage-symbol-copy">
        {formatTimestamp(entry.recorded_at)}
      </p>
    </td>
  );
}
