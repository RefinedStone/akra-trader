// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationActionLeafSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationActionLeafSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationCommitControlLeafSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationCommitControlLeafSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  const {} = model;

  return (
    <td>
      <div className="market-data-provenance-history-actions">
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationActionLeafSection
          model={model}
          plan={plan}
        />
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationCommitControlLeafSection
          model={model}
          plan={plan}
        />
      </div>
    </td>
  );
}
