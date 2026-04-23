// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyTemplateAuditFilterSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateAuditFilterSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateAuditTableSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateAuditTableSection";

export function RuntimeProviderProvenanceGovernancePolicyTemplateAuditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Policy template team audit</strong>
        <p>Filter shared audit events by template, action, or actor to review who changed governance defaults.</p>
      </div>
      <RuntimeProviderProvenanceGovernancePolicyTemplateAuditFilterSection model={model} />
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsLoading ? (
        <p className="empty-state">Loading policy template audit trail…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError ? (
        <p className="market-data-workflow-feedback">
          Policy template audit load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits.length ? (
        <RuntimeProviderProvenanceGovernancePolicyTemplateAuditTableSection model={model} />
      ) : (
        <p className="empty-state">No policy template audit records match the current filter.</p>
      )}
    </div>
  );
}
