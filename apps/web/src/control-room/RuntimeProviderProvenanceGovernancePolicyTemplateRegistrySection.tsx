// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogWorkflowSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogWorkflowSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateAuditSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateAuditSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateDraftSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateDraftSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateRegistryTableSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateRegistryTableSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateVersionsSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateVersionsSection";

export function RuntimeProviderProvenanceGovernancePolicyTemplateRegistrySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceGovernancePolicyTemplateDraftSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogWorkflowSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyTemplateRegistryTableSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyTemplateVersionsSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyTemplateAuditSection model={model} />
    </>
  );
}
