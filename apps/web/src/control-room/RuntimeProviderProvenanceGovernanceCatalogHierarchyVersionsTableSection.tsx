// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowActionSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowActionSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowDetailSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowDetailSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionsTableSection({
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
          <th>Step</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.map((entry) => (
          <tr key={`${entry.revision.revision_id}:${entry.step.step_id ?? "step"}`}>
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowDetailSection entry={entry} />
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyVersionRowActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
