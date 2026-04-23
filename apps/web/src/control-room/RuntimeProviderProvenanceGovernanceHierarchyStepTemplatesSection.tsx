// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateDraftSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateDraftSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistrySection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistrySection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplatesSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Named hierarchy step templates</strong>
          <p>Promote a captured hierarchy step into a reusable template, version it, and bulk-govern it across policy catalogs.</p>
        </div>
        <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateDraftSection model={model} />
        <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistrySection model={model} />
        <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsSection model={model} />
        <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSection model={model} />
      </div>
    </>
  );
}
