// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueueBatchActionsSection } from "./RuntimeProviderProvenanceApprovalQueueBatchActionsSection";
import { RuntimeProviderProvenanceApprovalQueueFilterBarSection } from "./RuntimeProviderProvenanceApprovalQueueFilterBarSection";
import { RuntimeProviderProvenanceApprovalQueuePlansTableSection } from "./RuntimeProviderProvenanceApprovalQueuePlansTableSection";
import { RuntimeProviderProvenanceApprovalQueueSelectedPlanDetailSection } from "./RuntimeProviderProvenanceApprovalQueueSelectedPlanDetailSection";

export function RuntimeProviderProvenanceApprovalQueueCard({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-workspace-card">
      <div className="market-data-provenance-history-head">
        <strong>Approval queue</strong>
        <p>Review staged scheduler governance plans by lane and priority, approve them, then apply or roll back against the captured revision snapshot.</p>
      </div>
      <div className="provider-provenance-governance-summary">
        <strong>
          Pending {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.pending_approval_count} · Ready {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.ready_to_apply_count} · Completed {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.completed_count}
        </strong>
        <span>
          Filtered queue rows: {filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length} of {providerProvenanceSchedulerNarrativeGovernanceQueueSummary.total}
        </span>
      </div>
      <RuntimeProviderProvenanceApprovalQueueBatchActionsSection model={model} />
      <RuntimeProviderProvenanceApprovalQueueFilterBarSection model={model} />
      <RuntimeProviderProvenanceApprovalQueuePlansTableSection model={model} />
      <RuntimeProviderProvenanceApprovalQueueSelectedPlanDetailSection model={model} />
    </div>
  );
}
