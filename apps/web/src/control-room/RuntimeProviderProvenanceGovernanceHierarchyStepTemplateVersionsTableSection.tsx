// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowActionSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowActionSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowDetailSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowDetailSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionsTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Revision</th>
          <th>Template</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateHistory.history.map((entry) => (
          <tr key={entry.revision_id}>
            <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowDetailSection entry={entry} />
            <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateVersionRowActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
