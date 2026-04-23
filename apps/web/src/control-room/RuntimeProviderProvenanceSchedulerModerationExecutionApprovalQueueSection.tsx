// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationExecutionApprovalQueueSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
