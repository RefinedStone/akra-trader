// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicyDraftTargetsSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (providerProvenanceSchedulerExportPolicyDraft.routing_policy_id !== "custom") {
    return null;
  }

  return (
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
  );
}
