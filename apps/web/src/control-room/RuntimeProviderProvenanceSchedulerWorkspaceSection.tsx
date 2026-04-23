// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerAutomationSection } from "./RuntimeProviderProvenanceSchedulerAutomationSection";
import { RuntimeProviderProvenanceSchedulerExportsSection } from "./RuntimeProviderProvenanceSchedulerExportsSection";
import { RuntimeProviderProvenanceSchedulerModerationSection } from "./RuntimeProviderProvenanceSchedulerModerationSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceSection";

export function RuntimeProviderProvenanceSchedulerWorkspaceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerAnalyticsLoading && !providerProvenanceSchedulerAnalytics ? (
        <p className="empty-state">Loading scheduler automation trends…</p>
      ) : null}
      {providerProvenanceSchedulerAnalyticsError ? (
        <p className="market-data-workflow-feedback">
          Scheduler automation analytics failed: {providerProvenanceSchedulerAnalyticsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerHistoryError ? (
        <p className="market-data-workflow-feedback">
          Scheduler automation history failed: {providerProvenanceSchedulerHistoryError}
        </p>
      ) : null}
      {providerProvenanceSchedulerCurrent ? (
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
      ) : null}
    </>
  );
}
