// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Stitched report governance registries</strong>
        <p>
          Save the stitched-report-only approval queue slice and default policy layer as
          a dedicated lifecycle object, then reapply or restore it without reopening the
          shared governance workspace.
        </p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Lag stitched governance"
            type="text"
            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="Queue slice and default policy bundle"
            type="text"
            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.description}
          />
        </label>
        <label>
          <span>Default policy template</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                ...current,
                default_policy_template_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.default_policy_template_id}
          >
            <option value="">No default policy template</option>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
              .filter((entry) =>
                providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                  entry.item_type_scope,
                  "stitched_report_view",
                ),
              )
              .map((entry) => (
                <option key={entry.policy_template_id} value={entry.policy_template_id}>
                  {entry.name}
                </option>
              ))}
          </select>
        </label>
        <label>
          <span>Default policy catalog</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
                ...current,
                default_policy_catalog_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.default_policy_catalog_id}
          >
            <option value="">No default policy catalog</option>
            {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
              <option key={entry.catalog_id} value={entry.catalog_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <div className="market-data-provenance-history-actions">
          <button
            className="ghost-button"
            onClick={() => {
              void saveCurrentProviderProvenanceSchedulerStitchedReportGovernanceRegistry();
            }}
            type="button"
          >
            {editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId
              ? "Update registry"
              : "Save registry"}
          </button>
          {editingProviderProvenanceSchedulerStitchedReportGovernanceRegistryId ? (
            <button
              className="ghost-button"
              onClick={() => {
                resetProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft();
              }}
              type="button"
            >
              Cancel edit
            </button>
          ) : null}
        </div>
      </div>
      <div className="filter-bar">
        <label>
          <span>Search</span>
          <input
            onChange={(event) => {
              setProviderProvenanceSchedulerStitchedReportGovernanceRegistrySearch(
                event.target.value,
              );
            }}
            placeholder="registry, queue, policy"
            type="text"
            value={providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch}
          />
        </label>
      </div>
    </>
  );
}
