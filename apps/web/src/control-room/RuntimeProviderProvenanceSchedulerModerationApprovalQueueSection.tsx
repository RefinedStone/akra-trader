// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerCatalogGovernanceApprovalQueueSection } from "./RuntimeProviderProvenanceSchedulerCatalogGovernanceApprovalQueueSection";
import { RuntimeProviderProvenanceSchedulerModerationExecutionApprovalQueueSection } from "./RuntimeProviderProvenanceSchedulerModerationExecutionApprovalQueueSection";
import { RuntimeProviderProvenanceSchedulerModerationGovernanceApprovalQueueSection } from "./RuntimeProviderProvenanceSchedulerModerationGovernanceApprovalQueueSection";

export function RuntimeProviderProvenanceSchedulerModerationApprovalQueueSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerModerationGovernanceApprovalQueueSection model={model} />
      <RuntimeProviderProvenanceSchedulerCatalogGovernanceApprovalQueueSection model={model} />
      <RuntimeProviderProvenanceSchedulerModerationExecutionApprovalQueueSection model={model} />
    </>
  );
}
