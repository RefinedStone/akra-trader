// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchySection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchySection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplatesSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplatesSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogAuditSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogAuditSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateRegistrySection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateRegistrySection";

export function RuntimeProviderProvenanceGovernancePolicyTemplatesCard({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Governance policy templates</strong>
        <p>
          Save reusable approval-lane defaults, manage revisions, and review the shared audit
          trail for policy edits.
        </p>
      </div>
      <RuntimeProviderProvenanceGovernancePolicyTemplateRegistrySection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogSection model={model} />
      <RuntimeProviderProvenanceGovernanceCatalogHierarchySection model={model} />
      <RuntimeProviderProvenanceGovernanceHierarchyStepTemplatesSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogAuditSection model={model} />
    </div>
  );
}
