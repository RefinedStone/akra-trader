// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitControlsSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitControlsSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportBulkApprovalStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitControlsSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewSection model={model} />
    </>
  );
}
