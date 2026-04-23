// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkPolicyStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
