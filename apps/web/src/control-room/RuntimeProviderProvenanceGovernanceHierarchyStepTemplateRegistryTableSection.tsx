// @ts-nocheck
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowActionSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowActionSection";
import { RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowDetailSection } from "./RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowDetailSection";

export function RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <p className="run-lineage-symbol-copy">
        Target catalogs: {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds.length
          || (selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog ? 1 : 0)}
        {" "}selected for cross-catalog apply.
      </p>
      {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesLoading ? (
        <p className="empty-state">Loading hierarchy step templates…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesError ? (
        <p className="market-data-workflow-feedback">
          Hierarchy step template load failed: {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplatesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th aria-label="Select template">Sel</th>
              <th>Template</th>
              <th>Origin</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
              <tr key={entry.hierarchy_step_template_id}>
                <td>
                  <input
                    checked={selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIdSet.has(entry.hierarchy_step_template_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateSelection(
                        entry.hierarchy_step_template_id,
                      );
                    }}
                    type="checkbox"
                  />
                </td>
                <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowDetailSection entry={entry} />
                <RuntimeProviderProvenanceGovernanceHierarchyStepTemplateRegistryRowActionSection entry={entry} />
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No hierarchy step templates saved yet.</p>
      )}
    </>
  );
}
