// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditActorCellSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditActorCellSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSummaryCellSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSummaryCellSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTemplateCellSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTemplateCellSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTableSection({
  model,
}: {
  model: any;
}) {
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
        {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits.map((entry) => (
          <tr key={entry.audit_id}>
            <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditSummaryCellSection entry={entry} />
            <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditTemplateCellSection entry={entry} />
            <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateAuditActorCellSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
