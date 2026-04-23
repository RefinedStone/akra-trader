// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalPolicySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched report approval queue</strong>
          <p>
            Review saved stitched report view governance plans without leaving the stitched
            report surface. This keeps stitched-report approvals and policy defaults visible
            next to the saved lens they change.
          </p>
        </div>
        <div className="provider-provenance-governance-summary">
          <strong>
            {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.total} stitched plan(s)
          </strong>
          <span>
            {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.pending_approval_count} pending approval · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.ready_to_apply_count} ready to apply · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceQueueSummary.completed_count} completed
          </span>
        </div>
        <div className="filter-bar">
          <label>
            <span>Queue state</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  queue_state:
                    event.target.value === "pending_approval"
                    || event.target.value === "ready_to_apply"
                    || event.target.value === "completed"
                      ? event.target.value
                      : ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.queue_state}
            >
              <option value={ALL_FILTER_VALUE}>All states</option>
              <option value="pending_approval">Pending approval</option>
              <option value="ready_to_apply">Ready to apply</option>
              <option value="completed">Completed</option>
            </select>
          </label>
          <label>
            <span>Lane</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  approval_lane: event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.approval_lane}
            >
              <option value={ALL_FILTER_VALUE}>All lanes</option>
              {Array.from(
                new Set(
                  providerProvenanceSchedulerStitchedReportGovernancePlans.map(
                    (entry) => entry.approval_lane,
                  ),
                ),
              ).sort().map((lane) => (
                <option key={lane} value={lane}>
                  {formatWorkflowToken(lane)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Priority</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  approval_priority: event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.approval_priority}
            >
              <option value={ALL_FILTER_VALUE}>All priorities</option>
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>
          <label>
            <span>Policy template</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  policy_template_id:
                    event.target.value === ""
                      ? ""
                      : event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_template_id}
            >
              <option value={ALL_FILTER_VALUE}>All policy templates</option>
              <option value="">No policy template</option>
              {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                .filter(
                  (entry) =>
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
            <span>Policy catalog</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  policy_catalog_id:
                    event.target.value === ""
                      ? ""
                      : event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_catalog_id}
            >
              <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
              <option value="">No policy catalog</option>
              {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
                <option key={entry.catalog_id} value={entry.catalog_id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Search</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
              placeholder="plan, view, policy"
              type="text"
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.search}
            />
          </label>
          <label>
            <span>Sort</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
                  ...current,
                  sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                    event.target.value,
                  ),
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.sort}
            >
              <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
                Queue priority
              </option>
              <option value="updated_desc">Updated newest</option>
              <option value="updated_asc">Updated oldest</option>
              <option value="created_desc">Created newest</option>
              <option value="created_asc">Created oldest</option>
            </select>
          </label>
        </div>
        {providerProvenanceSchedulerStitchedReportGovernancePlansLoading ? (
          <p className="empty-state">Loading stitched report approval queue…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernancePlansError ? (
          <p className="market-data-workflow-feedback">
            Stitched report approval queue failed: {providerProvenanceSchedulerStitchedReportGovernancePlansError}
          </p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernancePlans.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Plan</th>
                <th>Preview</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerStitchedReportGovernancePlans.map((plan) => (
                <tr key={`provider-scheduler-stitched-governance-plan-${plan.plan_id}`}>
                  <td>
                    <strong>
                      {formatWorkflowToken(plan.action)} stitched_report_view
                    </strong>
                    <p className="run-lineage-symbol-copy">
                      {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}
                      {plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}
                      {plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
                    </p>
                    {plan.policy_guidance ? (
                      <p className="run-lineage-symbol-copy">{plan.policy_guidance}</p>
                    ) : null}
                  </td>
                  <td>
                    <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
                    <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
                    <p className="run-lineage-symbol-copy">
                      {plan.preview_items.length} preview row(s) · rollback ready {plan.rollback_ready_count}
                    </p>
                  </td>
                  <td>
                    <div className="market-data-provenance-history-actions">
                      <button
                        className="ghost-button"
                        onClick={() => {
                          reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue(plan);
                        }}
                        type="button"
                      >
                        {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
                          ? "Shared queue selected"
                          : "Review in shared queue"}
                      </button>
                      <button
                        className="ghost-button"
                        disabled={
                          plan.status !== "previewed"
                          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                        }
                        onClick={() => {
                          void approveProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                        }}
                        type="button"
                      >
                        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
                          ? "Approving…"
                          : "Approve"}
                      </button>
                      <button
                        className="ghost-button"
                        disabled={
                          plan.status !== "approved"
                          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                        }
                        onClick={() => {
                          void applyProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                        }}
                        type="button"
                      >
                        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
                          ? "Applying…"
                          : "Apply"}
                      </button>
                      <button
                        className="ghost-button"
                        disabled={
                          plan.status !== "applied"
                          || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
                        }
                        onClick={() => {
                          void rollbackProviderProvenanceSchedulerNarrativeGovernancePlanEntry(plan);
                        }}
                        type="button"
                      >
                        {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
                          ? "Rolling back…"
                          : "Rollback"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !providerProvenanceSchedulerStitchedReportGovernancePlansLoading
            ? <p className="empty-state">No stitched report governance plans match the dedicated queue filters.</p>
            : null
        )}
      </div>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched report policy catalogs</strong>
          <p>
            Review only governance catalogs that can drive stitched report view approval
            defaults, then apply those defaults or jump into the shared catalog workspace.
          </p>
        </div>
        <div className="provider-provenance-governance-summary">
          <strong>
            {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length} stitched catalog(s)
          </strong>
          <span>
            {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter((entry) => entry.status === "active").length} active · {" "}
            {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter((entry) => entry.status === "deleted").length} deleted
          </span>
        </div>
        <div className="filter-bar">
          <label>
            <span>Search</span>
            <input
              onChange={(event) => {
                setProviderProvenanceSchedulerStitchedReportGovernanceCatalogSearch(
                  event.target.value,
                );
              }}
              placeholder="catalog, guidance, policy"
              type="text"
              value={providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch}
            />
          </label>
        </div>
        {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Catalog</th>
                <th>Defaults</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((catalog) => (
                <tr key={`provider-scheduler-stitched-governance-catalog-${catalog.catalog_id}`}>
                  <td>
                    <strong>{catalog.name}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(catalog.status)} · {catalog.policy_template_ids.length} linked template(s)
                    </p>
                    <p className="run-lineage-symbol-copy">
                      Scope {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {catalog.description || "No stitched report catalog description recorded."}
                    </p>
                  </td>
                  <td>
                    <strong>
                      {catalog.default_policy_template_name ?? "No default policy template"}
                    </strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {catalog.hierarchy_steps.length} hierarchy step(s)
                    </p>
                    {catalog.guidance ? (
                      <p className="run-lineage-symbol-copy">{catalog.guidance}</p>
                    ) : null}
                  </td>
                  <td>
                    <div className="market-data-provenance-history-actions">
                      <button
                        className="ghost-button"
                        disabled={catalog.status !== "active"}
                        onClick={() => {
                          applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
                        }}
                        type="button"
                      >
                        Use defaults
                      </button>
                      <button
                        className="ghost-button"
                        disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
                        onClick={() => {
                          applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(catalog);
                          void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
                        }}
                        type="button"
                      >
                        Stage queue
                      </button>
                      <button
                        className="ghost-button"
                        onClick={() => {
                          openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(catalog);
                        }}
                        type="button"
                      >
                        Open shared catalog
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty-state">No stitched report policy catalogs match the current search.</p>
        )}
      </div>
    </>
  );
}

