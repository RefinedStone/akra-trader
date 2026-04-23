// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyTemplateAuditActorCellSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateAuditActorCellSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateAuditSummaryCellSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateAuditSummaryCellSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateAuditTemplateCellSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateAuditTemplateCellSection";

export function RuntimeProviderProvenanceGovernancePolicyTemplateAuditTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Audit</th>
          <th>Template</th>
          <th>Actor</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits.map((entry) => (
          <tr key={entry.audit_id}>
            <RuntimeProviderProvenanceGovernancePolicyTemplateAuditSummaryCellSection entry={entry} />
            <RuntimeProviderProvenanceGovernancePolicyTemplateAuditTemplateCellSection entry={entry} />
            <RuntimeProviderProvenanceGovernancePolicyTemplateAuditActorCellSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
