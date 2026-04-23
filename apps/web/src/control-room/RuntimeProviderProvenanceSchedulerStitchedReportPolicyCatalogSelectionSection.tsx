// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogActionCellSection model={model}>
      <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionStateSection
        catalog={catalog}
        model={model}
      />
    </RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogActionCellSection>
  );
}
