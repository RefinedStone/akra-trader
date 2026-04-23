// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyCatalogSelectorSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyCatalogSelectorSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyTemplateSelectorSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyTemplateSelectorSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetSelectionSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyTemplateSelectorSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueuePolicyCatalogSelectorSection model={model} />
    </>
  );
}
