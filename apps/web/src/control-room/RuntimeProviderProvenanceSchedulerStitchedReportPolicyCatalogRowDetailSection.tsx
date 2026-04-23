// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDefaultBodySection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDefaultBodySection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogRowDetailSection({
  model,
  catalog,
  SelectionSection,
}: {
  model: any;
  catalog: any;
  SelectionSection: any;
}) {
  const {} = model;

  return (
    <tr>
      <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogStateSection
        catalog={catalog}
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDefaultBodySection
        catalog={catalog}
        model={model}
      />
      <SelectionSection catalog={catalog} model={model} />
    </tr>
  );
}
