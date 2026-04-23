// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueSelectedPlanPreviewDetailSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <table className="data-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Diff preview</th>
            <th>Rollback</th>
          </tr>
        </thead>
        <tbody>
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.map((item) => (
            <tr key={item.item_id}>
              <td>
                <strong>{item.item_name ?? item.item_id}</strong>
                <p className="run-lineage-symbol-copy">
                  {formatWorkflowToken(item.outcome)} · {formatWorkflowToken(item.status ?? "unknown")}
                </p>
                <p className="run-lineage-symbol-copy">
                  {item.message ?? "No preview note."}
                </p>
              </td>
              <td>
                <strong>
                  {item.changed_fields.length ? item.changed_fields.join(", ") : "No field changes"}
                </strong>
                {item.changed_fields.length ? (
                  <div className="provider-provenance-governance-summary">
                    {item.changed_fields.map((fieldName) => (
                      <span key={fieldName}>
                        {fieldName}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.before)} {"->"}{" "}
                        {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.after)}
                      </span>
                    ))}
                  </div>
                ) : null}
              </td>
              <td>
                <strong>
                  {item.rollback_revision_id
                    ? shortenIdentifier(item.rollback_revision_id, 10)
                    : "No rollback revision"}
                </strong>
                <p className="run-lineage-symbol-copy">
                  current {item.current_revision_id ? shortenIdentifier(item.current_revision_id, 10) : "n/a"}
                </p>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result ? (
        <p className="run-lineage-symbol-copy">
          Apply result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result)}
        </p>
      ) : null}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result ? (
        <p className="run-lineage-symbol-copy">
          Rollback result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result)}
        </p>
      ) : null}
    </>
  );
}
