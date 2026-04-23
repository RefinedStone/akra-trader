// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneSelectorSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneSelectorSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePrioritySelectorSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePrioritySelectorSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSelectorSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSelectorSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueFilterSelectSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSelectorSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneSelectorSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePrioritySelectorSection model={model} />
    </>
  );
}
