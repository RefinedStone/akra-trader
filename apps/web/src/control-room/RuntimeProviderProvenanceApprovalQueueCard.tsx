// @ts-nocheck
export function RuntimeProviderProvenanceApprovalQueueCard({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Approval queue</strong>
        <p>Review staged scheduler governance plans by lane and priority, approve them, then apply or roll back against the captured revision snapshot.</p>
      </div>
      <div className="provider-provenance-governance-summary">
        <strong>
          Pending {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.pending_approval_count} · Ready {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.ready_to_apply_count} · Completed {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.completed_count}
        </strong>
        <span>
          Filtered queue rows: {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} of {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.total}
        </span>
      </div>
      <div className="provider-provenance-governance-editor">
        <div className="market-data-provenance-history-head">
          <strong>Batch queue actions</strong>
          <p>Approve or apply multiple governance plans at once after filtering the queue to the exact lane, priority, or policy template slice you want.</p>
        </div>
        <div className="provider-provenance-governance-summary">
          <strong>
            Selected {selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} of {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} filtered plan(s)
          </strong>
          <span>
            {selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.map((plan) => shortenIdentifier(plan.plan_id, 8)).join(", ") || "No plans selected"}
          </span>
        </div>
        <div className="market-data-provenance-history-actions">
          <button
            className="ghost-button"
            onClick={toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections}
            type="button"
          >
            {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length > 0
              && selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length === filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length
              ? "Clear filtered"
              : "Select filtered"}
          </button>
          <button
            className="ghost-button"
            disabled={!selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length || providerProvenanceSchedulerNarrativeGovernanceBatchAction !== null}
            onClick={() => {
              void runProviderProvenanceSchedulerNarrativeGovernancePlanBatch("approve");
            }}
            type="button"
          >
            {providerProvenanceSchedulerNarrativeGovernanceBatchAction === "approve"
              ? "Approving…"
              : "Approve selected"}
          </button>
          <button
            className="ghost-button"
            disabled={!selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length || providerProvenanceSchedulerNarrativeGovernanceBatchAction !== null}
            onClick={() => {
              void runProviderProvenanceSchedulerNarrativeGovernancePlanBatch("apply");
            }}
            type="button"
          >
            {providerProvenanceSchedulerNarrativeGovernanceBatchAction === "apply"
              ? "Applying…"
              : "Apply selected"}
          </button>
        </div>
      </div>
      <div className="filter-bar">
        <label>
          <span>Queue state</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                queue_state:
                  event.target.value === "pending_approval"
                  || event.target.value === "ready_to_apply"
                  || event.target.value === "completed"
                    ? event.target.value
                    : ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.queue_state}
          >
            <option value={ALL_FILTER_VALUE}>All queue states</option>
            <option value="pending_approval">Pending approval</option>
            <option value="ready_to_apply">Ready to apply</option>
            <option value="completed">Completed</option>
          </select>
        </label>
        <label>
          <span>Item type</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                item_type:
                  event.target.value === "template"
                  || event.target.value === "registry"
                  || event.target.value === "stitched_report_view"
                  || event.target.value === "stitched_report_governance_registry"
                    ? event.target.value
                    : ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.item_type}
          >
            <option value={ALL_FILTER_VALUE}>All item types</option>
            <option value="template">Templates</option>
            <option value="registry">Registry</option>
            <option value="stitched_report_view">Stitched report views</option>
            <option value="stitched_report_governance_registry">Stitched governance registries</option>
          </select>
        </label>
        <label>
          <span>Lane</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                approval_lane: event.target.value || ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.approval_lane}
          >
            <option value={ALL_FILTER_VALUE}>All lanes</option>
            {Array.from(new Set(providerProvenanceSchedulerNarrativeGovernancePlans.map((entry) => entry.approval_lane))).sort().map((lane) => (
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
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                approval_priority: event.target.value || ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.approval_priority}
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
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                policy_template_id:
                  event.target.value === ""
                    ? ""
                    : event.target.value || ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.policy_template_id}
          >
            <option value={ALL_FILTER_VALUE}>All policy templates</option>
            <option value="">No policy template</option>
            {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates.map((entry) => (
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
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                policy_catalog_id:
                  event.target.value === ""
                    ? ""
                    : event.target.value || ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.policy_catalog_id}
          >
            <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
            <option value="">No policy catalog</option>
            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((entry) => (
              <option key={entry.catalog_id} value={entry.catalog_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Source template</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                source_hierarchy_step_template_id:
                  event.target.value === ""
                    ? ""
                    : event.target.value || ALL_FILTER_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.source_hierarchy_step_template_id}
          >
            <option value={ALL_FILTER_VALUE}>All source templates</option>
            <option value="">No source template</option>
            {providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates.map((entry) => (
              <option key={entry.hierarchy_step_template_id} value={entry.hierarchy_step_template_id}>
                {entry.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Search</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                search: event.target.value,
              }))
            }
            placeholder="plan, template, hierarchy"
            type="text"
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.search}
          />
        </label>
        <label>
          <span>Sort</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeGovernanceQueueFilter((current) => ({
                ...current,
                sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                  event.target.value,
                ),
              }))
            }
            value={providerProvenanceSchedulerNarrativeGovernanceQueueFilter.sort}
          >
            <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
              Queue priority
            </option>
            <option value="updated_desc">Updated newest</option>
            <option value="updated_asc">Updated oldest</option>
            <option value="created_desc">Created newest</option>
            <option value="created_asc">Created oldest</option>
            <option value="source_template_asc">Source template A-Z</option>
            <option value="source_template_desc">Source template Z-A</option>
          </select>
        </label>
      </div>
      {providerProvenanceSchedulerNarrativeGovernancePlansLoading ? (
        <p className="empty-state">Loading governance plans…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePlansError ? (
        <p className="market-data-workflow-feedback">
          Governance plan registry load failed: {providerProvenanceSchedulerNarrativeGovernancePlansError}
        </p>
      ) : null}
      {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all filtered governance plans"
                  checked={
                    filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length > 0
                    && selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans.length === filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length
                  }
                  onChange={toggleAllFilteredProviderProvenanceSchedulerNarrativeGovernancePlanSelections}
                  type="checkbox"
                />
              </th>
              <th>Plan</th>
              <th>Preview</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.map((plan) => (
              <tr
                key={plan.plan_id}
                className={
                  selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id
                    ? "active-row"
                    : undefined
                }
              >
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select governance plan ${plan.plan_id}`}
                    checked={selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet.has(plan.plan_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeGovernancePlanSelection(plan.plan_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <td>
                  <strong>
                    {formatWorkflowToken(plan.action)} {plan.item_type}
                  </strong>
                  <p className="run-lineage-symbol-copy">
                    {shortenIdentifier(plan.plan_id, 10)} · {formatWorkflowToken(getProviderProvenanceSchedulerNarrativeGovernanceQueueState(plan))}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {plan.created_by_tab_label ?? plan.created_by_tab_id ?? "unknown tab"} · {formatTimestamp(plan.updated_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(plan.approval_lane)} · {formatWorkflowToken(plan.approval_priority)}{plan.policy_template_name ? ` · ${plan.policy_template_name}` : ""}{plan.policy_catalog_name ? ` · ${plan.policy_catalog_name}` : ""}
                  </p>
                  {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(plan) ? (
                    <p className="run-lineage-symbol-copy">
                      {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(plan)}
                    </p>
                  ) : null}
                  {plan.policy_catalog_name ? (
                    <p className="run-lineage-symbol-copy">
                      Source catalog {plan.policy_catalog_name}
                    </p>
                  ) : null}
                  {plan.source_hierarchy_step_template_name || plan.source_hierarchy_step_template_id ? (
                    <p className="run-lineage-symbol-copy">
                      Source hierarchy step template {plan.source_hierarchy_step_template_name ?? plan.source_hierarchy_step_template_id}
                    </p>
                  ) : null}
                </td>
                <td>
                  <strong>{formatProviderProvenanceSchedulerNarrativeGovernancePlanSummary(plan)}</strong>
                  <p className="run-lineage-symbol-copy">{plan.rollback_summary}</p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      onClick={() => {
                        setSelectedProviderProvenanceSchedulerNarrativeGovernancePlanId(plan.plan_id);
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerNarrativeGovernancePlanId === plan.plan_id ? "Selected" : "Inspect"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No scheduler governance plans match the current approval queue filters.</p>
      )}
      {selectedProviderProvenanceSchedulerNarrativeGovernancePlan ? (
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Selected plan</strong>
            <p>
              {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.action)} {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.item_type} ·{" "}
              {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status)} ·{" "}
              {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.length} preview row(s)
            </p>
          </div>
          <div className="provider-provenance-governance-summary">
            <strong>{selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_summary}</strong>
            <span>
              {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approval_lane)} · {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approval_priority)}
              {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_template_name
                ? ` · ${selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_template_name}`
                : ""}{" "}
              {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_catalog_name
                ? ` · ${selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_catalog_name}`
                : ""}{" "}
              ·{" "}
              Approval {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approved_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.approved_at) : "pending"} ·{" "}
              Apply {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_at) : "not applied"} ·{" "}
              Rollback {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rolled_back_at ? formatTimestamp(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rolled_back_at) : "not rolled back"}
            </span>
          </div>
          {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(selectedProviderProvenanceSchedulerNarrativeGovernancePlan) ? (
            <p className="run-lineage-symbol-copy">
              Hierarchy: {formatProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyPosition(selectedProviderProvenanceSchedulerNarrativeGovernancePlan)}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_guidance ? (
            <p className="run-lineage-symbol-copy">
              Guidance: {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.policy_guidance}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_name
          || selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_id ? (
            <p className="run-lineage-symbol-copy">
              Source hierarchy step template: {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_name
                ?? selectedProviderProvenanceSchedulerNarrativeGovernancePlan.source_hierarchy_step_template_id}
            </p>
          ) : null}
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              disabled={
                selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "previewed"
                || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
              }
              onClick={() => {
                void approveProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeGovernancePlanAction === "approve"
                ? "Approving…"
                : "Approve plan"}
            </button>
            <button
              className="ghost-button"
              disabled={
                selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "approved"
                || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
              }
              onClick={() => {
                void applyProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeGovernancePlanAction === "apply"
                ? "Applying…"
                : "Apply approved plan"}
            </button>
            <button
              className="ghost-button"
              disabled={
                selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status !== "applied"
                || providerProvenanceSchedulerNarrativeGovernancePlanAction !== null
              }
              onClick={() => {
                void rollbackProviderProvenanceSchedulerNarrativeGovernanceSelectedPlan();
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeGovernancePlanAction === "rollback"
                ? "Rolling back…"
                : "Rollback plan"}
            </button>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Diff preview</th>
                <th>Rollback</th>
              </tr>
            </thead>
            <tbody>
              {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.map((item) => (
                <tr key={item.item_id}>
                  <td>
                    <strong>{item.item_name ?? item.item_id}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(item.outcome)} · {formatWorkflowToken(item.status ?? "unknown")}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {item.message ?? "No preview note."}
                    </p>
                  </td>
                  <td>
                    <strong>
                      {item.changed_fields.length ? item.changed_fields.join(", ") : "No field changes"}
                    </strong>
                    {item.changed_fields.length ? (
                      <div className="provider-provenance-governance-summary">
                        {item.changed_fields.map((fieldName) => (
                          <span key={fieldName}>
                            {fieldName}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.before)} {"->"}{" "}
                            {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(item.field_diffs[fieldName]?.after)}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </td>
                  <td>
                    <strong>
                      {item.rollback_revision_id
                        ? shortenIdentifier(item.rollback_revision_id, 10)
                        : "No rollback revision"}
                    </strong>
                    <p className="run-lineage-symbol-copy">
                      current {item.current_revision_id ? shortenIdentifier(item.current_revision_id, 10) : "n/a"}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result ? (
            <p className="run-lineage-symbol-copy">
              Apply result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.applied_result)}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result ? (
            <p className="run-lineage-symbol-copy">
              Rollback result: {formatProviderProvenanceSchedulerNarrativeBulkGovernanceFeedback(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.rollback_result)}
            </p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
