// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetApplySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetActionSection model={model} />
    </>
  );
}
