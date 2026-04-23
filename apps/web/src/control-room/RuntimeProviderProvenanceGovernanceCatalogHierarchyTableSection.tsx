// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyRowActionSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyRowActionSection";
import { RuntimeProviderProvenanceGovernanceCatalogHierarchyRowDetailSection } from "./RuntimeProviderProvenanceGovernanceCatalogHierarchyRowDetailSection";

export function RuntimeProviderProvenanceGovernanceCatalogHierarchyTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th aria-label="Select step">Sel</th>
          <th>Step</th>
          <th>Patch</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.map((step, index) => (
          <tr key={step.step_id ?? `${step.item_type}-${index}`}>
            <td>
              <input
                checked={step.step_id ? selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet.has(step.step_id) : false}
                disabled={!step.step_id}
                onChange={() => {
                  if (step.step_id) {
                    toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelection(step.step_id);
                  }
                }}
                type="checkbox"
              />
            </td>
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyRowDetailSection index={index} step={step} />
            <RuntimeProviderProvenanceGovernanceCatalogHierarchyRowActionSection step={step} />
          </tr>
        ))}
      </tbody>
    </table>
  ) : (
    <p className="empty-state">No hierarchy steps are currently captured on this policy catalog.</p>
  );
}
