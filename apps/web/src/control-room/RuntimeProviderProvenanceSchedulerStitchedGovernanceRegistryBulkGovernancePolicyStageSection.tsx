// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkGovernancePolicyStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
