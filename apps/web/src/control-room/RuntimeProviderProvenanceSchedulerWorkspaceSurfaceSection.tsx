// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerAutomationSection } from "./RuntimeProviderProvenanceSchedulerAutomationSection";
import { RuntimeProviderProvenanceSchedulerExportsSection } from "./RuntimeProviderProvenanceSchedulerExportsSection";
import { RuntimeProviderProvenanceSchedulerModerationSection } from "./RuntimeProviderProvenanceSchedulerModerationSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceSection";

export function RuntimeProviderProvenanceSchedulerWorkspaceSurfaceSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (!providerProvenanceSchedulerCurrent) {
    return null;
  }

  return (
    <div
      className={`market-data-provenance-shared-history ${
        providerProvenanceDashboardLayout.highlight_panel === "scheduler_alerts"
          ? "is-highlighted"
          : ""
      }`.trim()}
      ref={providerProvenanceSchedulerAutomationRef}
    >
      <RuntimeProviderProvenanceSchedulerAutomationSection model={model} />
      <RuntimeProviderProvenanceSchedulerModerationSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedGovernanceSection model={model} />
      <RuntimeProviderProvenanceSchedulerExportsSection model={model} />
    </div>
  );
}
