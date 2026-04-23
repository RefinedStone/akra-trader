// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSelectionSection";

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
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.status)} · revisions {entry.revision_count}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.description || "No stitched governance registry description recorded."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.default_policy_template_name ?? "No default policy template"}
                    {entry.default_policy_catalog_name
                      ? ` · ${entry.default_policy_catalog_name}`
                      : ""}
                  </p>
                </td>
                <td>
                  <strong>
                    {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                      entry.queue_view,
                    ) ?? "All stitched governance plans"}
                  </strong>
                  <p className="run-lineage-symbol-copy">
                    Saved {formatTimestamp(entry.updated_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
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
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryListingSection>
  );
}
