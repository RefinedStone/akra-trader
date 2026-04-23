// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportsRegistrySummarySection } from "./RuntimeProviderProvenanceSchedulerExportsRegistrySummarySection";
import { RuntimeProviderProvenanceSchedulerExportsRegistryTableSection } from "./RuntimeProviderProvenanceSchedulerExportsRegistryTableSection";

export function RuntimeProviderProvenanceSchedulerExportsRegistrySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerExportsRegistrySummarySection model={model} />
      <RuntimeProviderProvenanceSchedulerExportsRegistryTableSection model={model} />
    </>
  );
}
