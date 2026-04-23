// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueueSelectedPlanPreviewDetailSection } from "./RuntimeProviderProvenanceApprovalQueueSelectedPlanPreviewDetailSection";
import { RuntimeProviderProvenanceApprovalQueueSelectedPlanReviewSection } from "./RuntimeProviderProvenanceApprovalQueueSelectedPlanReviewSection";

export function RuntimeProviderProvenanceApprovalQueueSelectedPlanDetailSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return selectedProviderProvenanceSchedulerNarrativeGovernancePlan ? (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Selected plan</strong>
        <p>
          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.action)} {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.item_type} ·{" "}
          {formatWorkflowToken(selectedProviderProvenanceSchedulerNarrativeGovernancePlan.status)} ·{" "}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePlan.preview_items.length} preview row(s)
        </p>
      </div>
      <RuntimeProviderProvenanceApprovalQueueSelectedPlanReviewSection model={model} />
      <RuntimeProviderProvenanceApprovalQueueSelectedPlanPreviewDetailSection model={model} />
    </div>
  ) : null;
}
