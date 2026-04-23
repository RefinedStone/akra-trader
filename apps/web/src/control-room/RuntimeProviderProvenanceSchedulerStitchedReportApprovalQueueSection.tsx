// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection model={model} />
    </div>
  );
}
