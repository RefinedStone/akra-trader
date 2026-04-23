// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowActionSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowActionSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowDetailSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowDetailSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogVersionsTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Revision</th>
          <th>Defaults</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory.history.map((entry) => (
          <tr key={entry.revision_id}>
            <RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowDetailSection entry={entry} />
            <RuntimeProviderProvenanceGovernancePolicyCatalogVersionRowActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
