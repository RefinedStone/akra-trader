// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueueCard } from "./RuntimeProviderProvenanceApprovalQueueCard";
import { RuntimeProviderProvenanceAnalyticsPresetsCard } from "./RuntimeProviderProvenanceAnalyticsPresetsCard";
import { RuntimeProviderProvenanceDashboardLayoutCard } from "./RuntimeProviderProvenanceDashboardLayoutCard";
import { RuntimeProviderProvenanceDashboardViewsCard } from "./RuntimeProviderProvenanceDashboardViewsCard";
import { RuntimeProviderProvenanceScheduledReportsCard } from "./RuntimeProviderProvenanceScheduledReportsCard";
import { RuntimeProviderProvenanceGovernancePolicyTemplatesCard } from "./RuntimeProviderProvenanceGovernancePolicyTemplatesCard";
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryCard } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryCard";
import { RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard } from "./RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard";

export function RuntimeProviderProvenanceWorkspaceCards({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceDashboardLayoutCard model={model} />
      <RuntimeProviderProvenanceGovernancePolicyTemplatesCard model={model} />
      <RuntimeProviderProvenanceAnalyticsPresetsCard model={model} />
      <RuntimeProviderProvenanceDashboardViewsCard model={model} />
      <RuntimeProviderProvenanceScheduledReportsCard model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeTemplatesCard model={model} />
      <RuntimeProviderProvenanceSchedulerNarrativeRegistryCard model={model} />
      <RuntimeProviderProvenanceApprovalQueueCard model={model} />
    </>
  );
}
