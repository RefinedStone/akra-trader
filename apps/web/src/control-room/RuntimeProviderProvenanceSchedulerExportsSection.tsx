// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportAuditHistorySection } from "./RuntimeProviderProvenanceSchedulerExportAuditHistorySection";
import { RuntimeProviderProvenanceSchedulerExportsRegistrySection } from "./RuntimeProviderProvenanceSchedulerExportsRegistrySection";

export function RuntimeProviderProvenanceSchedulerExportsSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerExportsRegistrySection model={model} />
      <RuntimeProviderProvenanceSchedulerExportAuditHistorySection model={model} />
    </>
  );
}
