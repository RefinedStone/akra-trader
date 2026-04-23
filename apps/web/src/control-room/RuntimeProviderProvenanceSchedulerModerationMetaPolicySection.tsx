// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationMetaPolicySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
                <div className="market-data-provenance-history-head">
                  <strong>Moderation governance meta-policies</strong>
                  <p>
                    Save reusable review defaults for moderation governance policies, then
                    stage selected policy updates through a dedicated approval queue.
                  </p>
                </div>
                <div className="market-data-provenance-history-actions">
                  <label className="run-form-field">
                    <span>Name</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          name: event.target.value,
                        }));
                      }}
                      placeholder="Review moderation governance defaults"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Queue action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.action_scope}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          action_scope: event.target.value,
                        }));
                      }}
                    >
                      <option value="any">Any action</option>
                      <option value="update">Update only</option>
                      <option value="delete">Delete only</option>
                      <option value="restore">Restore only</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Policy action</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_action_scope}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          policy_action_scope: event.target.value,
                        }));
                      }}
                    >
                      <option value="any">Any action</option>
                      <option value="update">Update only</option>
                      <option value="delete">Delete only</option>
                      <option value="restore">Restore only</option>
                    </select>
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Approval note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_approval_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          require_approval_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Policy note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_require_approval_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          policy_require_approval_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          description: event.target.value,
                        }));
                      }}
                      placeholder="Reusable defaults for moderation governance policy review."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Queue guidance</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          guidance: event.target.value,
                        }));
                      }}
                      placeholder="Require an explicit note before approval."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.guidance}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Policy guidance</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          policy_guidance: event.target.value,
                        }));
                      }}
                      placeholder="Apply these defaults to selected governance policies."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_guidance}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name prefix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          name_prefix: event.target.value,
                        }));
                      }}
                      placeholder="[Reviewed] "
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_prefix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Name suffix</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          name_suffix: event.target.value,
                        }));
                      }}
                      placeholder=" / approved"
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_suffix}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Description append</span>
                    <input
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          description_append: event.target.value,
                        }));
                      }}
                      placeholder=" Reviewed in moderation governance queue."
                      type="text"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description_append}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Outcome</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.default_moderation_status}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          default_moderation_status: event.target.value,
                        }));
                      }}
                    >
                      <option value="approved">Approved</option>
                      <option value="pending">Pending</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Governance view</span>
                    <select
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.governance_view}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          governance_view: event.target.value,
                        }));
                      }}
                    >
                      <option value="all_feedback">All feedback</option>
                      <option value="pending_queue">Pending queue</option>
                      <option value="high_score_pending">High-score pending</option>
                    </select>
                  </label>
                  <label className="run-form-field">
                    <span>Window days</span>
                    <input
                      min={7}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          window_days: Number(event.target.value) || 0,
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.window_days}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Stale pending hours</span>
                    <input
                      min={1}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          stale_pending_hours: Number(event.target.value) || 0,
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.stale_pending_hours}
                    />
                  </label>
                  <label className="run-form-field">
                    <span>Minimum score</span>
                    <input
                      min={0}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          minimum_score: Number(event.target.value) || 0,
                        }));
                      }}
                      type="number"
                      value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.minimum_score}
                    />
                  </label>
                  <label className="run-form-field checkbox-field">
                    <span>Require moderator note</span>
                    <input
                      checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_note}
                      onChange={(event) => {
                        setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                          ...current,
                          require_note: event.target.checked,
                        }));
                      }}
                      type="checkbox"
                    />
                  </label>
                  <button
                    className="ghost-button"
                    disabled={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesLoading}
                    onClick={() => {
                      void createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry();
                    }}
                    type="button"
                  >
                    Save meta-policy
                  </button>
                </div>
                {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError ? (
                  <p className="market-data-workflow-feedback">
                    Moderation governance meta-policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError}
                  </p>
                ) : null}
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Meta-policy</th>
                      <th>Defaults</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items.length ? (
                      providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies.items.map((entry) => (
                        <tr key={`provider-scheduler-search-moderation-governance-meta-policy-${entry.meta_policy_id}`}>
                          <td>
                            <strong>{entry.name}</strong>
                            <p className="run-lineage-symbol-copy">
                              Queue {formatWorkflowToken(entry.action_scope)} · note {entry.require_approval_note ? "required" : "optional"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.guidance || entry.description || "No meta-governance guidance"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Saved {formatTimestamp(entry.updated_at)} · {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                            </p>
                          </td>
                          <td>
                            <p className="run-lineage-symbol-copy">
                              Policy {formatWorkflowToken(entry.policy_action_scope ?? "any")} · note {entry.policy_require_approval_note ? "required" : "optional"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Outcome {formatWorkflowToken(entry.default_moderation_status ?? "approved")} · view {formatWorkflowToken(entry.governance_view ?? "pending_queue")}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Window {entry.window_days ?? 0}d · stale {entry.stale_pending_hours ?? 0}h · minimum {entry.minimum_score ?? 0}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.name_prefix || entry.name_suffix
                                ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                                : "No name affixes"}
                            </p>
                          </td>
                          <td>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                onClick={() => {
                                  applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDefaults(entry);
                                }}
                                type="button"
                              >
                                Use defaults
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3}>
                          <p className="empty-state">No moderation governance meta-policies saved yet.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
    </>
  );
}
