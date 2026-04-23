// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowActionSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowActionSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowDetailSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowDetailSection";

export function RuntimeProviderProvenanceGovernancePolicyTemplateVersionsTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Revision</th>
          <th>Scope</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory.history.map((entry) => (
          <tr key={entry.revision_id}>
            <RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowDetailSection entry={entry} />
            <RuntimeProviderProvenanceGovernancePolicyTemplateVersionRowActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
