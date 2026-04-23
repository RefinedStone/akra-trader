// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportPolicySummaryChipsSection } from "./RuntimeProviderProvenanceSchedulerExportPolicySummaryChipsSection";
import { RuntimeProviderProvenanceSchedulerExportPolicySummaryCopySection } from "./RuntimeProviderProvenanceSchedulerExportPolicySummaryCopySection";

export function RuntimeProviderProvenanceSchedulerExportPolicySummarySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerExportPolicySummaryChipsSection model={model} />
      <RuntimeProviderProvenanceSchedulerExportPolicySummaryCopySection model={model} />
    </>
  );
}
