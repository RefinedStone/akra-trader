// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkHistoryLimitControlsSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkHistoryLimitControlsSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkSliceLimitControlsSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkSliceLimitControlsSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitControlsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkSliceLimitControlsSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkHistoryLimitControlsSection model={model} />
    </>
  );
}
