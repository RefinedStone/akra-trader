// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationApprovalQueueSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
                <div className="market-data-provenance-history-head">
                  <strong>Moderation governance approval queue</strong>
                  <p>
                    Stage selected moderation governance policies, preview the exact policy diffs,
                    then approve and apply the change set.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.action}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                          ...current,
                          action: event.target.value,
                        }));
                      }}
                    >
                      <option value="update">Update</option>
                      <option value="delete">Delete</option>
                      <option value="restore">Restore</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Reusable meta-policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.meta_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                          ...current,
                          meta_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>Inline policy patch</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-meta-policy-option-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Approval/apply note</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                          ...current,
                          note: event.target.value,
                        }));
                      }}
                      placeholder="required when the meta-policy gates approval on notes"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.note}
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId !== null
                    }
                    onClick={() => {
                      void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaSelection();
                    }}
                    type="button"
                  >
                    Stage selected policies
                  </button>
                  <label className="run-form-field">
                    <span>Queue state</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.queue_state}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                          ...current,
                          queue_state: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All states</option>
                      <option value="pending_approval">Pending approval</option>
                      <option value="ready_to_apply">Ready to apply</option>
                      <option value="completed">Completed</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Meta-policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.meta_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                          ...current,
                          meta_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All meta-policies</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.available_filters.meta_policies ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-meta-plan-policy-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <span className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.completed_count ?? 0} completed
                  </span>
                </div>
                {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError ? (
                  <p className="market-data-workflow-feedback">
                    Moderation governance approval queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError}
                  </p>
                ) : null}
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Preview</th>
                      <th>Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-governance-meta-plan-${entry.plan_id}`}>
                          <td>
                            <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.action)} · {entry.meta_policy_name ?? "Inline defaults"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                            </p>
                            {entry.guidance ? (
                              <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{entry.preview_count} preview item(s)</strong>
                            {entry.preview_items.slice(0, 4).map((preview) => (
                              <div key={`provider-scheduler-search-moderation-governance-meta-preview-${entry.plan_id}-${preview.governance_policy_id}`}>
                                <p className="run-lineage-symbol-copy">
                                  {preview.governance_policy_name} · {formatWorkflowToken(preview.outcome)}
                                  {preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                                  {preview.message ? ` · ${preview.message}` : ""}
                                </p>
                                {Object.entries(preview.field_diffs).slice(0, 2).map(([field, diff]) => (
                                  <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-governance-meta-diff-${entry.plan_id}-${preview.governance_policy_id}-${field}`}>
                                    {field}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.before)} → {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.after)}
                                  </p>
                                ))}
                              </div>
                            ))}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                            </p>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "pending_approval"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "ready_to_apply"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                                }}
                                type="button"
                              >
                                Apply
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">No moderation governance meta-plans match the current filter.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <div className="market-data-provenance-history-head">
                  <strong>Moderation catalog governance queue</strong>
                  <p>
                    Stage selected moderation policy catalogs, preview the exact catalog diffs,
                    then approve and apply the change set.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.action}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                          ...current,
                          action: event.target.value,
                        }));
                      }}
                    >
                      <option value="update">Update</option>
                      <option value="delete">Delete</option>
                      <option value="restore">Restore</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.governance_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                          ...current,
                          governance_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>No reusable policy</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-policy-option-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Approval/apply note</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                          ...current,
                          note: event.target.value,
                        }));
                      }}
                      placeholder="required when the governance policy gates approval on notes"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.note}
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                      || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId !== null
                    }
                    onClick={() => {
                      void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceSelection();
                    }}
                    type="button"
                  >
                    Stage selected catalogs
                  </button>
                  <label className="run-form-field">
                    <span>Queue state</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.queue_state}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                          ...current,
                          queue_state: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All states</option>
                      <option value="pending_approval">Pending approval</option>
                      <option value="ready_to_apply">Ready to apply</option>
                      <option value="completed">Completed</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance policy</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.governance_policy_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                          ...current,
                          governance_policy_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All policies</option>
                      {(providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.available_filters.governance_policies ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-moderation-governance-queue-policy-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <span className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.completed_count ?? 0} completed
                  </span>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Preview</th>
                      <th>Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernancePlans.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-catalog-governance-plan-${entry.plan_id}`}>
                          <td>
                            <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                            <p className="run-lineage-symbol-copy">
                              {formatWorkflowToken(entry.action)} · {entry.governance_policy_name ?? "No policy"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                            </p>
                            {entry.guidance ? (
                              <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{entry.preview_count} preview item(s)</strong>
                            {entry.preview_items.slice(0, 4).map((preview) => (
                              <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-catalog-governance-preview-${entry.plan_id}-${preview.catalog_id}`}>
                                {preview.catalog_name} · {formatWorkflowToken(preview.outcome)}{preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                                {preview.message ? ` · ${preview.message}` : ""}
                              </p>
                            ))}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                            </p>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "pending_approval"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "ready_to_apply"
                                  || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Apply
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">No moderation catalog governance plans match the current filter.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <div className="market-data-provenance-history-head">
                  <strong>Scheduler moderation approval queue</strong>
                  <p>
                    Stage selected feedback, review the plan preview, then approve and apply it
                    as a governed moderation batch.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Stage policy catalog</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationStageDraft.policy_catalog_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                          ...current,
                          policy_catalog_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>No catalog</option>
                      {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-stage-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Fallback outcome</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationStageDraft.moderation_status}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                          ...current,
                          moderation_status: event.target.value,
                        }));
                      }}
                    >
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="pending">Pending</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Approval/apply note</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                          ...current,
                          note: event.target.value,
                        }));
                      }}
                      placeholder="required by policy catalogs that gate approval on notes"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationStageDraft.note}
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                      || providerProvenanceSchedulerSearchModerationPlanPendingId !== null
                    }
                    onClick={() => {
                      void stageProviderProvenanceSchedulerSearchModerationSelection();
                    }}
                    type="button"
                  >
                    Stage selected feedback
                  </button>
                  <label className="run-form-field">
                    <span>Queue state</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationQueueFilter.queue_state}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                          ...current,
                          queue_state: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All states</option>
                      <option value="pending_approval">Pending approval</option>
                      <option value="ready_to_apply">Ready to apply</option>
                      <option value="completed">Completed</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Policy catalog</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationQueueFilter.policy_catalog_id}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                          ...current,
                          policy_catalog_id: event.target.value,
                        }));
                      }}
                    >
                      <option value={ALL_FILTER_VALUE}>All catalogs</option>
                      {(providerProvenanceSchedulerSearchModerationPlans?.available_filters.policy_catalogs ?? []).map((entry) => (
                        <option key={`provider-scheduler-search-queue-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                          {entry.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <span className="run-lineage-symbol-copy">
                    {providerProvenanceSchedulerSearchModerationPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationPlans?.summary.completed_count ?? 0} completed
                  </span>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Preview</th>
                      <th>Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationPlans?.items.length ? (
                      providerProvenanceSchedulerSearchModerationPlans.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-plan-${entry.plan_id}`}>
                          <td>
                            <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                            <p className="run-lineage-symbol-copy">
                              {entry.policy_catalog_name ?? "No catalog"} · {formatWorkflowToken(entry.proposed_moderation_status)}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Eligible {entry.feedback_ids.length}/{entry.requested_feedback_ids.length} · minimum score {entry.minimum_score}
                            </p>
                          </td>
                          <td>
                            <strong>{entry.preview_count} preview item(s)</strong>
                            {entry.preview_items.slice(0, 4).map((preview) => (
                              <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-preview-${entry.plan_id}-${preview.feedback_id}`}>
                                {preview.occurrence_id} · {formatWorkflowToken(preview.current_moderation_status)} → {formatWorkflowToken(preview.proposed_moderation_status)} · score {preview.score} · {preview.eligible ? "eligible" : "skipped"}
                                {preview.reason_tags.length ? ` · ${preview.reason_tags.join(" · ")}` : ""}
                              </p>
                            ))}
                            {entry.missing_feedback_ids.length ? (
                              <p className="run-lineage-symbol-copy">
                                Missing {entry.missing_feedback_ids.join(" · ")}
                              </p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                            </p>
                            {entry.approval_note ? (
                              <p className="run-lineage-symbol-copy">{entry.approval_note}</p>
                            ) : null}
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "pending_approval"
                                  || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void approveProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={
                                  entry.queue_state !== "ready_to_apply"
                                  || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                                }
                                onClick={() => {
                                  void applyProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                                }}
                                type="button"
                              >
                                Apply
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">
                            No staged scheduler moderation plans match the current queue filter.
                          </p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
    </>
  );
}
