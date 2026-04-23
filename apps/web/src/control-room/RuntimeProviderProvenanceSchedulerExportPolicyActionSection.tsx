// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportPolicyApprovalEscalationActionSection } from "./RuntimeProviderProvenanceSchedulerExportPolicyApprovalEscalationActionSection";
import { RuntimeProviderProvenanceSchedulerExportPolicySaveActionSection } from "./RuntimeProviderProvenanceSchedulerExportPolicySaveActionSection";

export function RuntimeProviderProvenanceSchedulerExportPolicyActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="market-data-provenance-history-actions">
      <RuntimeProviderProvenanceSchedulerExportPolicySaveActionSection model={model} />
      <RuntimeProviderProvenanceSchedulerExportPolicyApprovalEscalationActionSection model={model} />
    </div>
  );
}
