// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueToggleResetSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection model={model} />
    </>
  );
}
