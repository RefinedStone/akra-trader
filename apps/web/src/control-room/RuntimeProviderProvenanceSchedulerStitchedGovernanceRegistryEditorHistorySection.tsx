// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryEditorHistorySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
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
        {providerProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
          <div className="provider-provenance-governance-bar">
            <div className="provider-provenance-governance-summary">
              <strong>
                {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length} selected
              </strong>
              <span>
                {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries.filter((entry) => entry.status === "active").length} active · {" "}
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
        {providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading ? (
          <p className="empty-state">Loading stitched governance registries…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistriesError ? (
          <p className="market-data-workflow-feedback">
            Stitched governance registries failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistriesError}
          </p>
        ) : null}
        {filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>
                  <input
                    aria-label="Select all stitched governance registries"
                    checked={
                      providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
                      > 0
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
              {filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries.map((entry) => (
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
                      <button
                        className="ghost-button"
                        onClick={() => {
                          void toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory(
                            entry.registry_id,
                          );
                        }}
                        type="button"
                      >
                        {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryId === entry.registry_id
                          && selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory
                          ? "Hide versions"
                          : "Versions"}
                      </button>
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
        ) : (
          !providerProvenanceSchedulerStitchedReportGovernanceRegistriesLoading
            ? <p className="empty-state">No stitched governance registries match the current search.</p>
            : null
        )}
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Stitched governance registry team audit</strong>
            <p>
              Review registry lifecycle and bulk governance changes by registry, actor, or
              reason without leaving the stitched-report governance surface.
            </p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Registry</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                    ...current,
                    registry_id: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.registry_id}
              >
                <option value="">All registries</option>
                {providerProvenanceSchedulerStitchedReportGovernanceRegistries.map((entry) => (
                  <option key={entry.registry_id} value={entry.registry_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Action</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                    ...current,
                    action: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.action}
              >
                <option value={ALL_FILTER_VALUE}>All actions</option>
                <option value="created">Created</option>
                <option value="updated">Updated</option>
                <option value="deleted">Deleted</option>
                <option value="restored">Restored</option>
              </select>
            </label>
            <label>
              <span>Actor tab</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                    ...current,
                    actor_tab_id: event.target.value,
                  }))
                }
                placeholder="tab_ops"
                type="text"
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.actor_tab_id}
              />
            </label>
            <label>
              <span>Search</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
                    ...current,
                    search: event.target.value,
                  }))
                }
                placeholder="lag reviewed"
                type="text"
                value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.search}
              />
            </label>
          </div>
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading ? (
            <p className="empty-state">Loading stitched governance registry audit…</p>
          ) : null}
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError ? (
            <p className="market-data-workflow-feedback">
              Stitched governance registry audit failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsError}
            </p>
          ) : null}
          {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.length ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Action</th>
                  <th>Actor</th>
                  <th>Detail</th>
                </tr>
              </thead>
              <tbody>
                {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.map((entry) => (
                  <tr key={`provider-scheduler-stitched-governance-registry-audit-${entry.audit_id}`}>
                    <td>
                      <strong>{formatTimestamp(entry.recorded_at)}</strong>
                      <p className="run-lineage-symbol-copy">{entry.name}</p>
                    </td>
                    <td>
                      <strong>{formatWorkflowToken(entry.action)}</strong>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.status)} · {" "}
                        {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                          entry.queue_view,
                        ) ?? "All stitched governance plans"}
                      </p>
                    </td>
                    <td>
                      <strong>{entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}</strong>
                      <p className="run-lineage-symbol-copy">
                        {entry.actor_tab_id ?? "No tab id recorded."}
                      </p>
                    </td>
                    <td>
                      <strong>{entry.detail}</strong>
                      <p className="run-lineage-symbol-copy">{entry.reason}</p>
                      <p className="run-lineage-symbol-copy">
                        {entry.default_policy_template_name ?? "No default policy template"}
                        {entry.default_policy_catalog_name
                          ? ` · ${entry.default_policy_catalog_name}`
                          : ""}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            !providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditsLoading
              ? <p className="empty-state">No stitched governance registry audit events match the selected filters.</p>
              : null
          )}
        </div>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryLoading ? (
          <p className="empty-state">Loading stitched governance registry history…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError ? (
          <p className="market-data-workflow-feedback">
            Registry history failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryHistoryError}
          </p>
        ) : null}
        {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Recorded</th>
                <th>Snapshot</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory.history.map((entry) => (
                <tr key={`provider-scheduler-stitched-governance-registry-revision-${entry.revision_id}`}>
                  <td>
                    <strong>{formatTimestamp(entry.recorded_at)}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                    </p>
                  </td>
                  <td>
                    <strong>{entry.name}</strong>
                    <p className="run-lineage-symbol-copy">{entry.description || "No description recorded."}</p>
                    <p className="run-lineage-symbol-copy">
                      {formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary(
                        entry.queue_view,
                      ) ?? "All stitched governance plans"}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {entry.default_policy_template_name ?? "No default policy template"}
                      {entry.default_policy_catalog_name
                        ? ` · ${entry.default_policy_catalog_name}`
                        : ""}
                    </p>
                  </td>
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
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </div>
    </>
  );
}

