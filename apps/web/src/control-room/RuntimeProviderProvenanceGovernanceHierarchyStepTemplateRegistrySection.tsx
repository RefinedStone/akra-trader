// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkSelectionStageSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkSelectionStageSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkStepStageSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkStepStageSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryTableSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryTableSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistrySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkSelectionStageSection model={model} />
      <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateBulkStepStageSection model={model} />
      <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryTableSection model={model} />
    </>
  );
}
