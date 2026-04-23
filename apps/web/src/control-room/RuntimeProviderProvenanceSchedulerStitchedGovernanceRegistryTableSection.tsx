// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowDetailSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableSection({ model }: { model: any }) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection model={model}>
      {(entries: any[]) => (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all stitched governance registries"
                  checked={
                    providerProvenanceSchedulerStitchedReportGovernanceRegistries.length > 0
                    && selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                    === providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections}
                  type="checkbox"
                />
              </th>
              <th>Registry</th>
              <th>Queue slice</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={`provider-scheduler-stitched-governance-registry-${entry.registry_id}`}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select stitched governance registry ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet.has(entry.registry_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelection(
                        entry.registry_id,
                      );
                    }}
                    type="checkbox"
                  />
                </td>
                <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowDetailSection
                  entry={entry}
                  model={model}
                />
                <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowActionCellSection
                  entry={entry}
                  model={model}
                />
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection>
  );
}
