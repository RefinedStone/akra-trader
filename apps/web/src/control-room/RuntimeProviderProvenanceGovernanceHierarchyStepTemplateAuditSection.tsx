// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditFilterSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditFilterSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTableSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTableSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Hierarchy step template team audit</strong>
          <p>Filter lifecycle and bulk-governance events by template, action, or actor to review who changed reusable cross-catalog steps.</p>
        </div>
        <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditFilterSection model={model} />
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsLoading ? (
          <p className="empty-state">Loading hierarchy step template audit trail…</p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError ? (
          <p className="market-data-workflow-feedback">
            Hierarchy step template audit load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditsError}
          </p>
        ) : null}
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits.length ? (
          <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTableSection model={model} />
        ) : (
          <p className="empty-state">No hierarchy step template audit records match the current filter.</p>
        )}
      </div>
    </>
  );
}
