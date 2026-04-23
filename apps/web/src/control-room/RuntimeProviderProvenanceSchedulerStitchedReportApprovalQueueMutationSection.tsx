// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitControlSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitControlSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionSection";

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
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionSection
          model={model}
          plan={plan}
        />
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitControlSection
          model={model}
          plan={plan}
        />
      </div>
    </td>
  );
}
