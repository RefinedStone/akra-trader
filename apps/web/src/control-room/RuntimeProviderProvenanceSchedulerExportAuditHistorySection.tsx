// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportAuditHistorySummarySection } from "./RuntimeProviderProvenanceSchedulerExportAuditHistorySummarySection";
import { RuntimeProviderProvenanceSchedulerExportAuditHistoryTableSection } from "./RuntimeProviderProvenanceSchedulerExportAuditHistoryTableSection";
import { RuntimeProviderProvenanceSchedulerExportPolicySection } from "./RuntimeProviderProvenanceSchedulerExportPolicySection";

export function RuntimeProviderProvenanceSchedulerExportAuditHistorySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (!selectedProviderProvenanceSchedulerExportJobId) {
    return null;
  }

  return (
    <div className="market-data-provenance-shared-history">
      <RuntimeProviderProvenanceSchedulerExportAuditHistorySummarySection model={model} />
      <RuntimeProviderProvenanceSchedulerExportPolicySection model={model} />
      <RuntimeProviderProvenanceSchedulerExportAuditHistoryTableSection model={model} />
    </div>
  );
}
