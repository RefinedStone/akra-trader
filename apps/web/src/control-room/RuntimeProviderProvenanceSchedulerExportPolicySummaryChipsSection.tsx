// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicySummaryChipsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="run-filter-summary-chip-row">
      <span className="run-filter-summary-chip">
        Current route{" "}
        {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.routing_policy_id ?? "default")}
      </span>
      <span className="run-filter-summary-chip">
        Targets{" "}
        {selectedProviderProvenanceSchedulerExportEntry.routing_targets.length
          ? selectedProviderProvenanceSchedulerExportEntry.routing_targets.join(", ")
          : "none"}
      </span>
      <span className="run-filter-summary-chip">
        Approval {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.approval_state)}
      </span>
      {selectedProviderProvenanceSchedulerExportEntry.approved_at ? (
        <span className="run-filter-summary-chip">
          Approved {formatTimestamp(selectedProviderProvenanceSchedulerExportEntry.approved_at)} by{" "}
          {selectedProviderProvenanceSchedulerExportEntry.approved_by ?? "unknown"}
        </span>
      ) : null}
    </div>
  );
}
