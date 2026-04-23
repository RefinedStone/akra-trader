// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkApprovalStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkApprovalStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkPolicyStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkPolicyStageSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitPolicyStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkApprovalStageSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkPolicyStageSection model={model} />
    </>
  );
}
