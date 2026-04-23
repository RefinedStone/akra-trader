// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportAuditHistorySummarySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-head">
      <strong>Scheduler export audit trail</strong>
      <p>{shortenIdentifier(selectedProviderProvenanceSchedulerExportJobId, 10)}</p>
    </div>
  );
}
