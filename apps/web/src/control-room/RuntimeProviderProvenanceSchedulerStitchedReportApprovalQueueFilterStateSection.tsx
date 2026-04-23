// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueryInputSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueryInputSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueToggleResetSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueToggleResetSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterStateSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="filter-bar">
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueToggleResetSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueryInputSection model={model} />
    </div>
  );
}
