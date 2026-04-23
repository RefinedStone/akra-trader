// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalPolicySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSection model={model} />
    </>
  );
}
