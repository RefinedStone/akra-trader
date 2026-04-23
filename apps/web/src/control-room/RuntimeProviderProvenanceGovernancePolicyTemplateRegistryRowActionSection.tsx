// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyTemplateRegistryRowActionSection({
  entry,
}: {
  entry: any;
}) {
  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <button
          className="ghost-button"
          onClick={() => {
            if (entry.status !== "active") {
              return;
            }
            if (
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "template",
              )
            ) {
              setProviderProvenanceSchedulerNarrativeTemplateGovernancePolicyTemplateId(entry.policy_template_id);
            }
            if (
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "registry",
              )
            ) {
              setProviderProvenanceSchedulerNarrativeRegistryGovernancePolicyTemplateId(entry.policy_template_id);
            }
            if (
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "stitched_report_view",
              )
            ) {
              setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId(entry.policy_template_id);
            }
            if (
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "stitched_report_governance_registry",
              )
            ) {
              setProviderProvenanceSchedulerStitchedReportGovernanceRegistryGovernancePolicyTemplateId(
                entry.policy_template_id,
              );
            }
          }}
          disabled={entry.status !== "active"}
          type="button"
        >
          Use defaults
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            editProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(entry);
          }}
          type="button"
        >
          Edit
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void removeProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(entry);
          }}
          type="button"
        >
          Delete
        </button>
        <button
          className="ghost-button"
          onClick={() => {
            void toggleProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory(
              entry.policy_template_id,
            );
          }}
          type="button"
        >
          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateId === entry.policy_template_id
            && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateHistory
            ? "Hide versions"
            : "Versions"}
        </button>
      </div>
    </td>
  );
}
