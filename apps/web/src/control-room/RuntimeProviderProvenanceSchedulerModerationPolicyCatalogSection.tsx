// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerModerationCatalogLifecycleSection } from "./RuntimeProviderProvenanceSchedulerModerationCatalogLifecycleSection";
import { RuntimeProviderProvenanceSchedulerModerationGovernancePolicySection } from "./RuntimeProviderProvenanceSchedulerModerationGovernancePolicySection";
import { RuntimeProviderProvenanceSchedulerModerationMetaPolicySection } from "./RuntimeProviderProvenanceSchedulerModerationMetaPolicySection";

export function RuntimeProviderProvenanceSchedulerModerationPolicyCatalogSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerModerationCatalogLifecycleSection model={model} />
      <RuntimeProviderProvenanceSchedulerModerationGovernancePolicySection model={model} />
      <RuntimeProviderProvenanceSchedulerModerationMetaPolicySection model={model} />
    </>
  );
}
