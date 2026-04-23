// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionPerActionHandlersSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionPerActionHandlersSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSharedDispatchPlumbingSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSharedDispatchPlumbingSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionActionDispatchSection({
  model,
  catalog,
  children,
}: {
  model: any;
  catalog: any;
  children: any;
}) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSharedDispatchPlumbingSection
      catalog={catalog}
      model={model}
    >
      {({
        applyCatalogDefaults,
        openSharedCatalog,
        stageCatalogHierarchy,
      }: {
        applyCatalogDefaults: () => void;
        openSharedCatalog: () => void;
        stageCatalogHierarchy: () => void;
      }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionPerActionHandlersSection
          applyCatalogDefaults={applyCatalogDefaults}
          openSharedCatalog={openSharedCatalog}
          stageCatalogHierarchy={stageCatalogHierarchy}
        >
          {children}
        </RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionPerActionHandlersSection>
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSelectionSharedDispatchPlumbingSection>
  );
}
