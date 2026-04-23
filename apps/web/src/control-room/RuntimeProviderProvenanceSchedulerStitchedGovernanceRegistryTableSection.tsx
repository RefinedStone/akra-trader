// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowDetailSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowDetailSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableRowSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableRowSelectionSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableSection({ model }: { model: any }) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection model={model}>
      {(entries: any[]) => (
        <table className="data-table">
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSection
            model={model}
          />
          <tbody>
            {entries.map((entry) => (
              <tr key={`provider-scheduler-stitched-governance-registry-${entry.registry_id}`}>
                <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableRowSelectionSection
                  entry={entry}
                  model={model}
                />
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
