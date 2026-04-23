// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSelectionSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRowActionCellSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            applyProviderProvenanceSchedulerStitchedReportGovernanceRegistry(entry);
          }}
          type="button"
        >
          Apply
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            editProviderProvenanceSchedulerStitchedReportGovernanceRegistry(entry);
          }}
          type="button"
        >
          Edit
        </button>
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSelectionSection
          entry={entry}
          model={model}
        />
        <button
          className="ghost-button"
          disabled={entry.status !== "active"}
          onClick={() => {
            void deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry(
              entry,
            );
          }}
          type="button"
        >
          Delete
        </button>
      </div>
    </td>
  );
}
