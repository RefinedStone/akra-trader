// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableViewSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableViewSection";

export function RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const { providerProvenanceSchedulerNarrativeTemplates } = model;

  return providerProvenanceSchedulerNarrativeTemplates.length ? (
    <RuntimeProviderProvenanceSchedulerNarrativeTemplateRegistryTableViewSection model={model} />
  ) : (
    <p className="empty-state">No scheduler narrative templates saved yet.</p>
  );
}
