// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (!selectedProviderProvenanceSchedulerExportEntry) {
    return null;
  }

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Escalation policy</strong>
        <p>
          Save a per-export routing policy, require approval when needed, and then escalate the
          selected scheduler snapshot.
        </p>
      </div>
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
      {providerProvenanceSchedulerExportPolicyDraft.routing_policy_id === "custom" ? (
        <div className="filter-bar">
          {selectedProviderProvenanceSchedulerExportEntry.available_delivery_targets.map((target) => (
            <label className="provider-provenance-checkbox" key={`provider-scheduler-target-${target}`}>
              <input
                checked={providerProvenanceSchedulerExportPolicyDraft.delivery_targets.includes(target)}
                onChange={(event) =>
                  setProviderProvenanceSchedulerExportPolicyDraft((current) => ({
                    ...current,
                    delivery_targets: event.target.checked
                      ? Array.from(new Set([...current.delivery_targets, target]))
                      : current.delivery_targets.filter((candidate) => candidate !== target),
                  }))
                }
                type="checkbox"
              />
              <span>{target}</span>
            </label>
          ))}
        </div>
      ) : null}
      <div className="run-filter-summary-chip-row">
        <span className="run-filter-summary-chip">
          Current route{" "}
          {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.routing_policy_id ?? "default")}
        </span>
        <span className="run-filter-summary-chip">
          Targets{" "}
          {selectedProviderProvenanceSchedulerExportEntry.routing_targets.length
            ? selectedProviderProvenanceSchedulerExportEntry.routing_targets.join(", ")
            : "none"}
        </span>
        <span className="run-filter-summary-chip">
          Approval {formatWorkflowToken(selectedProviderProvenanceSchedulerExportEntry.approval_state)}
        </span>
        {selectedProviderProvenanceSchedulerExportEntry.approved_at ? (
          <span className="run-filter-summary-chip">
            Approved {formatTimestamp(selectedProviderProvenanceSchedulerExportEntry.approved_at)} by{" "}
            {selectedProviderProvenanceSchedulerExportEntry.approved_by ?? "unknown"}
          </span>
        ) : null}
      </div>
      <p className="market-data-workflow-export-copy">
        {selectedProviderProvenanceSchedulerExportEntry.routing_policy_summary ??
          "No routing summary recorded."}{" "}
        {selectedProviderProvenanceSchedulerExportEntry.approval_summary ??
          "No approval summary recorded."}
      </p>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            void updateSharedProviderProvenanceSchedulerExportPolicy(
              selectedProviderProvenanceSchedulerExportEntry,
            );
          }}
          type="button"
        >
          Save policy
        </button>
        <button
          className="ghost-button"
          disabled={
            !selectedProviderProvenanceSchedulerExportEntry.approval_required ||
            selectedProviderProvenanceSchedulerExportEntry.approval_state === "approved"
          }
          onClick={() => {
            void approveSharedProviderProvenanceSchedulerExport(
              selectedProviderProvenanceSchedulerExportEntry,
            );
          }}
          type="button"
        >
          Approve route
        </button>
        <button
          className="ghost-button"
          disabled={
            selectedProviderProvenanceSchedulerExportEntry.approval_required &&
            selectedProviderProvenanceSchedulerExportEntry.approval_state !== "approved"
          }
          onClick={() => {
            void escalateSharedProviderProvenanceSchedulerExport(
              selectedProviderProvenanceSchedulerExportEntry,
            );
          }}
          type="button"
        >
          Escalate now
        </button>
      </div>
    </div>
  );
}
