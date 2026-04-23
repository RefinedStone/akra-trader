// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerAlertReviewSection } from "./RuntimeProviderProvenanceSchedulerAlertReviewSection";
import { RuntimeProviderProvenanceSchedulerAlertTimelineSection } from "./RuntimeProviderProvenanceSchedulerAlertTimelineSection";
import { RuntimeProviderProvenanceSchedulerModerationGovernanceSection } from "./RuntimeProviderProvenanceSchedulerModerationGovernanceSection";

export function RuntimeProviderProvenanceSchedulerModerationSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerAlertReviewSection model={model} />
      <RuntimeProviderProvenanceSchedulerModerationGovernanceSection model={model} />
      <RuntimeProviderProvenanceSchedulerAlertTimelineSection model={model} />
    </>
  );
}
