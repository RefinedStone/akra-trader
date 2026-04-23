// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueueSelectedPlanApprovalActionSection } from "./RuntimeProviderProvenanceApprovalQueueSelectedPlanApprovalActionSection";
import { RuntimeProviderProvenanceApprovalQueueSelectedPlanSummarySection } from "./RuntimeProviderProvenanceApprovalQueueSelectedPlanSummarySection";

export function RuntimeProviderProvenanceApprovalQueueSelectedPlanReviewSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceApprovalQueueSelectedPlanSummarySection model={model} />
      <RuntimeProviderProvenanceApprovalQueueSelectedPlanApprovalActionSection model={model} />
    </>
  );
}
