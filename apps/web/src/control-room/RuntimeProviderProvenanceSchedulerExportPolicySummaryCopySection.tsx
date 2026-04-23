// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicySummaryCopySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <p className="market-data-workflow-export-copy">
      {selectedProviderProvenanceSchedulerExportEntry.routing_policy_summary ??
        "No routing summary recorded."}{" "}
      {selectedProviderProvenanceSchedulerExportEntry.approval_summary ??
        "No approval summary recorded."}
    </p>
  );
}
