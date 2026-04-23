// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowActionSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowActionSection";
import { RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowDetailSection } from "./RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowDetailSection";

export function RuntimeProviderProvenanceGovernancePolicyTemplateRegistryTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesLoading ? (
        <p className="empty-state">Loading governance policy templates…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesError ? (
        <p className="market-data-workflow-feedback">
          Governance policy template registry load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyTemplatesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all governance policy templates"
                  checked={
                    providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length > 0
                    && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds.length === providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelections}
                  type="checkbox"
                />
              </th>
              <th>Template</th>
              <th>Scope</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
              <tr key={entry.policy_template_id}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select governance policy template ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIdSet.has(entry.policy_template_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateSelection(entry.policy_template_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowDetailSection entry={entry} />
                <RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowActionSection entry={entry} />
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No governance policy templates saved yet.</p>
      )}
    </>
  );
}
