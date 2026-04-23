// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkPolicyStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <label>
      <span>Policy template</span>
      <select
        onChange={(event) => {
          setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId(
            event.target.value,
          );
        }}
        value={providerProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId}
      >
        <option value="">Default staged policy</option>
        {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
          .filter(
            (entry) =>
              entry.status === "active"
              && providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "stitched_report_view",
              ),
          )
          .map((entry) => (
            <option key={entry.policy_template_id} value={entry.policy_template_id}>
              {entry.name} · {formatWorkflowToken(entry.approval_lane)} ·{" "}
              {formatWorkflowToken(entry.approval_priority)}
            </option>
          ))}
      </select>
    </label>
  );
}
