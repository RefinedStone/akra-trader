// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicyDraftFormSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="filter-bar">
      <label>
        <span>Route</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
              ...current,
              routing_policy_id: event.target.value,
              delivery_targets:
                event.target.value === "custom"
                  ? current.delivery_targets.length
                    ? current.delivery_targets
                    : [...selectedProviderProvenanceSchedulerExportEntry.available_delivery_targets]
                  : current.delivery_targets,
            }))
          }
          value={providerProvenanceSchedulerExportPolicyDraft.routing_policy_id}
        >
          <option value="default">Default recommendation</option>
          <option value="chatops_only">Chatops only</option>
          <option value="all_targets">All targets</option>
          <option value="paging_only">Paging only</option>
          <option value="custom">Custom targets</option>
        </select>
      </label>
      <label>
        <span>Approval</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
              ...current,
              approval_policy_id:
                event.target.value === "manual_required" ? "manual_required" : "auto",
            }))
          }
          value={providerProvenanceSchedulerExportPolicyDraft.approval_policy_id}
        >
          <option value="auto">Auto</option>
          <option value="manual_required">Manual approval required</option>
        </select>
      </label>
      <label>
        <span>Approval note</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
              ...current,
              approval_note: event.target.value,
            }))
          }
          placeholder="manager_review_complete"
          type="text"
          value={providerProvenanceSchedulerExportPolicyDraft.approval_note}
        />
      </label>
    </div>
  );
}
