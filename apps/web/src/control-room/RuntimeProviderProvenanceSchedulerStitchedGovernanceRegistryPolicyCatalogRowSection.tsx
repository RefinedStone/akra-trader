// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogDefaultsDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogDefaultsDetailSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogDetailSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogRowSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogDetailSection
        catalog={catalog}
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogDefaultsDetailSection
        catalog={catalog}
        model={model}
      />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogActionSection
        catalog={catalog}
        model={model}
      />
    </>
  );
}
