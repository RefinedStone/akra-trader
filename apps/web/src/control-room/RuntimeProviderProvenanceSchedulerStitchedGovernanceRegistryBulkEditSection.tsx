// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkEditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
        <div className="provider-provenance-governance-bar">
          <div className="provider-provenance-governance-summary">
            <strong>
              {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length} selected
            </strong>
            <span>
              {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "active").length} active ·{" "}
              {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "deleted").length} deleted
            </span>
          </div>
          <div className="market-data-provenance-history-actions">
            <label>
              <span>Policy</span>
              <select
                onChange={(event) => {
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId(
                    event.target.value,
                  );
                }}
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId}
              >
                <option value="">No policy template</option>
                {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                  <option key={entry.policy_template_id} value={entry.policy_template_id}>
                    {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="ghost-button"
              onClick={toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections}
              type="button"
            >
              {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                === providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
                ? "Clear all"
                : "Select all"}
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
                  "delete",
                );
              }}
              type="button"
            >
              {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "delete"
                ? "Previewing…"
                : "Preview delete"}
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
                  "restore",
                );
              }}
              type="button"
            >
              {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "restore"
                ? "Previewing…"
                : "Preview restore"}
            </button>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Bulk stitched governance registry edits</strong>
            <p>
              Preview queue-slice, default-policy, and metadata changes as staged
              governance plans before approval and apply.
            </p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Name prefix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }))
                }
                placeholder="Ops / "
                type="text"
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.name_prefix}
              />
            </label>
            <label>
              <span>Name suffix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }))
                }
                placeholder=" / reviewed"
                type="text"
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.name_suffix}
              />
            </label>
            <label>
              <span>Description append</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }))
                }
                placeholder="shift-reviewed"
                type="text"
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.description_append}
              />
            </label>
            <label>
              <span>Queue state</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    queue_state: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.queue_state}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>All queue states</option>
                <option value="pending_approval">pending approval</option>
                <option value="ready_to_apply">ready to apply</option>
                <option value="completed">completed</option>
              </select>
            </label>
            <label>
              <span>Lane</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    approval_lane: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.approval_lane}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>Clear lane</option>
                <option value="chatops">chatops</option>
                <option value="ops">ops</option>
                <option value="leadership">leadership</option>
              </select>
            </label>
            <label>
              <span>Priority</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    approval_priority: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.approval_priority}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>Clear priority</option>
                <option value="low">low</option>
                <option value="normal">normal</option>
                <option value="high">high</option>
                <option value="critical">critical</option>
              </select>
            </label>
            <label>
              <span>Search</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    search: event.target.value,
                  }))
                }
                placeholder="keep current or blank to clear"
                type="text"
                value={
                  providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.search
                  === KEEP_CURRENT_BULK_GOVERNANCE_VALUE
                    ? ""
                    : providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.search
                }
              />
            </label>
            <label>
              <span>Sort</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    sort: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.sort}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>Clear sort</option>
                <option value="queue_priority">queue priority</option>
                <option value="updated_desc">updated newest</option>
                <option value="updated_asc">updated oldest</option>
                <option value="created_desc">created newest</option>
                <option value="created_asc">created oldest</option>
              </select>
            </label>
            <label>
              <span>Default policy template</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    default_policy_template_id: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.default_policy_template_id}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="">No default policy template</option>
                {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                  <option
                    key={entry.policy_template_id}
                    value={entry.policy_template_id}
                  >
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Default policy catalog</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
                    ...current,
                    default_policy_catalog_id: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.default_policy_catalog_id}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="">No default policy catalog</option>
                {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
                  <option key={entry.catalog_id} value={entry.catalog_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Governance policy</span>
              <select
                onChange={(event) => {
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId(
                    event.target.value,
                  );
                }}
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId}
              >
                <option value="">No policy template</option>
                {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                  <option key={entry.policy_template_id} value={entry.policy_template_id}>
                    {entry.name} · {formatWorkflowToken(entry.approval_lane)} · {formatWorkflowToken(entry.approval_priority)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Action</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={
                    !selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
                    || providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction
                    !== null
                  }
                  onClick={() => {
                    void runProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkGovernance(
                      "update",
                    );
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkAction === "update"
                    ? "Previewing…"
                    : "Preview bulk edit"}
                </button>
              </div>
            </label>
          </div>
        </div>
      ) : null}
    </>
  );
}
