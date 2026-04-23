// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetApplySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetApplySection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueToggleResetSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetApplySection model={model} />
    </>
  );
}
