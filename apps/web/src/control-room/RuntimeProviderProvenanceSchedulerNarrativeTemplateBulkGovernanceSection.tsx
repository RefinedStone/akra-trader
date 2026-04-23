// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkEditStageSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkEditStageSection";
import { RuntimeProviderProvenanceSchedulerNarrativeTemplateGovernanceBarSection } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplateGovernanceBarSection";

export function RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkGovernanceSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return providerProvenanceSchedulerNarrativeTemplates.length ? (
    <>
      <RuntimeProviderProvenanceSchedulerNarrativeTemplateGovernanceBarSection model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkEditStageSection model={model} />
    </>
  ) : null;
}
