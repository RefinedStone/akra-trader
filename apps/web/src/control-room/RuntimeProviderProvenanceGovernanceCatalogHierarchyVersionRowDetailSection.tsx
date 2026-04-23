// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowDetailSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <>
      <td>
        <strong>{entry.revision.revision_id}</strong>
        <p className="run-lineage-symbol-copy">{entry.revision.reason}</p>
        <p className="run-lineage-symbol-copy">{formatTimestamp(entry.revision.recorded_at)}</p>
      </td>
      <td>
        <strong>{entry.step.step_id ?? "unknown step"}</strong>
        <p className="run-lineage-symbol-copy">
          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
        </p>
        {entry.step.source_template_name || entry.step.source_template_id ? (
          <p className="run-lineage-symbol-copy">
            Source template: {entry.step.source_template_name ?? entry.step.source_template_id}
          </p>
        ) : null}
        <p className="run-lineage-symbol-copy">
          {entry.position} of {entry.total}
        </p>
      </td>
    </>
  );
}
