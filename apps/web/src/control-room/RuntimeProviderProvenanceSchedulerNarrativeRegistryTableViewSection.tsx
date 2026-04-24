// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection";
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryRowActionSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryRowActionSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryTableViewSection({
  model,
}: {
  model: any;
}) {
  const {
    providerProvenanceSchedulerNarrativeRegistryEntries,
    selectedProviderProvenanceSchedulerNarrativeRegistryIds,
    selectedProviderProvenanceSchedulerNarrativeRegistryIdSet,
    toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections,
    toggleProviderProvenanceSchedulerNarrativeRegistrySelection,
  } = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>
            <input
              aria-label="Select all scheduler narrative registry entries"
              checked={
                providerProvenanceSchedulerNarrativeRegistryEntries.length > 0
                && selectedProviderProvenanceSchedulerNarrativeRegistryIds.length === providerProvenanceSchedulerNarrativeRegistryEntries.length
              }
              onChange={toggleAllProviderProvenanceSchedulerNarrativeRegistrySelections}
              type="checkbox"
            />
          </th>
          <th>Registry</th>
          <th>Linked lens</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerNarrativeRegistryEntries.map((entry) => (
          <tr key={entry.registry_id}>
            <td className="provider-provenance-selection-cell">
              <input
                aria-label={`Select scheduler narrative registry ${entry.name}`}
                checked={selectedProviderProvenanceSchedulerNarrativeRegistryIdSet.has(entry.registry_id)}
                onChange={() => {
                  toggleProviderProvenanceSchedulerNarrativeRegistrySelection(entry.registry_id);
                }}
                type="checkbox"
              />
            </td>
            <RuntimeProviderProvenanceSchedulerNarrativeRegistryRowDetailSection entry={entry} model={model} />
            <RuntimeProviderProvenanceSchedulerNarrativeRegistryRowActionSection entry={entry} model={model} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
