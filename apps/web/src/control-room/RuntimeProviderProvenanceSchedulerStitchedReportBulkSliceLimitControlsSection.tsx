// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkOccurrenceLimitControlSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkOccurrenceLimitControlSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkResultLimitControlSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkResultLimitControlSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkWindowLimitControlSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkWindowLimitControlSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportBulkSliceLimitControlsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkWindowLimitControlSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkResultLimitControlSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkOccurrenceLimitControlSection model={model} />
    </>
  );
}
