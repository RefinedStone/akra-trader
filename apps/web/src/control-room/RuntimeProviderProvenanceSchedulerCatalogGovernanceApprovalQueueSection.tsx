// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerCatalogGovernanceApprovalQueueSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
