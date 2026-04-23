// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalPolicySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalPolicySection";
import { RuntimeProviderProvenanceSchedulerStitchedReportSavedViewSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportSavedViewSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportViewsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportSavedViewSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalPolicySection model={model} />
    </>
  );
}
