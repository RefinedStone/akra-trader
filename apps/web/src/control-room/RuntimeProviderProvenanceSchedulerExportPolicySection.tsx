// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportPolicyActionSection } from "./RuntimeProviderProvenanceSchedulerExportPolicyActionSection";
import { RuntimeProviderProvenanceSchedulerExportPolicyDraftSection } from "./RuntimeProviderProvenanceSchedulerExportPolicyDraftSection";
import { RuntimeProviderProvenanceSchedulerExportPolicySummarySection } from "./RuntimeProviderProvenanceSchedulerExportPolicySummarySection";

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
      <RuntimeProviderProvenanceSchedulerExportPolicyDraftSection model={model} />
      <RuntimeProviderProvenanceSchedulerExportPolicySummarySection model={model} />
      <RuntimeProviderProvenanceSchedulerExportPolicyActionSection model={model} />
    </div>
  );
}
