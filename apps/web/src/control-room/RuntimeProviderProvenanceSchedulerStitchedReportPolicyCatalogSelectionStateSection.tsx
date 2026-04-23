// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDerivedStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDerivedStateSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionStateSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDerivedStateSection catalog={catalog}>
      {({
        useDefaultsDisabled,
        stageQueueDisabled,
      }: {
        useDefaultsDisabled: boolean;
        stageQueueDisabled: boolean;
      }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionSection
          catalog={catalog}
          model={model}
          stageQueueDisabled={stageQueueDisabled}
          useDefaultsDisabled={useDefaultsDisabled}
        />
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDerivedStateSection>
  );
}
