// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection({
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
            applyProviderProvenanceSchedulerStitchedReportGovernanceRegistry(
              {
                ...selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory.registry,
                name: entry.name,
                description: entry.description,
                queue_view: entry.queue_view,
                default_policy_template_id: entry.default_policy_template_id,
                default_policy_template_name: entry.default_policy_template_name,
                default_policy_catalog_id: entry.default_policy_catalog_id,
                default_policy_catalog_name: entry.default_policy_catalog_name,
              },
            );
          }}
          type="button"
        >
          Apply snapshot
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistoryRevision(
              entry,
            );
          }}
          type="button"
        >
          Restore revision
        </button>
      </div>
    </td>
  );
}
