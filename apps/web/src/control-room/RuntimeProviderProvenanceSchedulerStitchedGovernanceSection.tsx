// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryLifecycleSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryLifecycleSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportViewsSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportViewsSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportViewsSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryLifecycleSection model={model} />
    </>
  );
}
